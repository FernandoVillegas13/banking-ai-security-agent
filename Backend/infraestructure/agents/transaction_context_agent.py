from domain.schema.schemas import AgentState
from datetime import datetime
from typing import Dict, Any, List

class TransactionContextAgent:
    def __init__(self):
        self.threshold = 2  # 2x del promedio para MONTO

    async def analyze_transaction(self, state: AgentState) -> AgentState:
        transaction = state['transaction_request']
        usual_behavior = state.get('usual_behavior')

        # Inicializar anomalías
        anomaly_signals = {
            "amount_anomaly": self.check_amount_anomaly(transaction, usual_behavior),
            "time_anomaly": self.check_time_anomaly(transaction, usual_behavior),
            "device_anomaly": self.check_device_anomaly(transaction, usual_behavior),
            "country_anomaly": self.check_country_anomaly(transaction, usual_behavior),
        }
        
        composite_risk = self.calculate_composite_risk(anomaly_signals)
        signals = self.collect_signals(anomaly_signals)
        
        anomaly_score = composite_risk
        
        agent_decision = {
            "agent_name": "transaction_context_agent",
            "status": "completed",
            "execution_time": datetime.utcnow().isoformat() + "Z",
            "anomaly_score": anomaly_score,
        }
        
        # Actualizar el estado
        state['anomaly_signals'] = anomaly_signals
        state["anomaly_score"] = anomaly_score
        state['signals'] = signals
        state['agent_audit'] = state.get('agent_audit', []) + [agent_decision]
        
        return state
    
    def check_amount_anomaly(self, transaction, usual_behavior: dict) -> Dict[str, Any]:
        if not usual_behavior:
            return {"is_anomaly": False, "score": 0.0, "reason": "No behavior data available"}
        
        usual_amount_avg = usual_behavior.usual_amount_avg
        amount = transaction.amount
        ratio = amount / usual_amount_avg if usual_amount_avg > 0 else 0
        
        is_anomaly = ratio > self.threshold
        score = min(ratio / self.threshold * 0.95, 1.0) if is_anomaly else ratio / self.threshold * 0.3
        
        return {
            "is_anomaly": is_anomaly,
            "score": round(score, 2),
            "threshold": self.threshold,
            "ratio": round(ratio, 2),
            "reason": f"Monto {ratio:.1f}x usual promedio" if is_anomaly else f"Monto dentro del rango normal ({ratio:.1f}x promedio)"
        }
    
    def check_time_anomaly(self, transaction, usual_behavior: dict) -> Dict[str, Any]:
        if not usual_behavior:
            return {"is_anomaly": False, "score": 0.0, "reason": "No behavior data available"}

        hour = transaction.timestamp.hour
        usual_hours = usual_behavior.usual_hours  # Ej: "09-22"
        try:
            # Parsear como rango: "09-22" -> 9 a 22
            start_hour, end_hour = map(int, str(usual_hours).split("-"))
            in_usual_hours = start_hour <= hour <= end_hour
            score = 0.1 if in_usual_hours else 0.85
            return {
                "is_anomaly": not in_usual_hours,
                "score": round(score, 2),
                "reason": f"Transacción a las {hour:02d}:00 es usual" if in_usual_hours else f"Transacción a las {hour:02d}:00 está fuera del rango {start_hour:02d}:00-{end_hour:02d}:00"
            }
        except Exception as e:
            return {"is_anomaly": False, "score": 0.0, "reason": f"Invalid hours format: {e}"}
    
    def check_device_anomaly(self, transaction, usual_behavior: dict) -> Dict[str, Any]:
        if not usual_behavior:
            return {"is_anomaly": False, "score": 0.0, "reason": "No behavior data available"}
        
        device_id = transaction.device_id
        usual_devices = usual_behavior.usual_devices.split(",") if isinstance(usual_behavior.usual_devices, str) else [usual_behavior.usual_devices]
        usual_devices = [d.strip() for d in usual_devices]
        
        device_match = device_id in usual_devices
        
        return {
            "is_anomaly": not device_match,
            "score": 0.05 if device_match else 0.85,
            "device_match": device_match,
            "reason": f"Dispositivo {device_id} es conocido y confiable" if device_match else f"Dispositivo {device_id} es nuevo/desconocido"
        }
    
    def check_country_anomaly(self, transaction, usual_behavior: dict) -> Dict[str, Any]:
        if not usual_behavior:
            return {"is_anomaly": False, "score": 0.0, "reason": "No behavior data available"}
        
        country = transaction.country
        usual_countries = usual_behavior.usual_countries.split(",") if isinstance(usual_behavior.usual_countries, str) else [usual_behavior.usual_countries]
        usual_countries = [c.strip() for c in usual_countries]
        
        country_match = country in usual_countries
        
        return {
            "is_anomaly": not country_match,
            "score": 0.05 if country_match else 0.75,
            "country_match": country_match,
            "reason": f"País {country} está en los países usuales" if country_match else f"País {country} es inusual"
        }
    
    def calculate_composite_risk(self, anomaly_signals: Dict) -> float:        
        # Contar cuántas anomalías fueron detectadas
        anomaly_count = sum(
            1 for anomaly_type in anomaly_signals.values()
            if anomaly_type.get("is_anomaly", False)
        )
        
        # Fórmula: qué tan alejado estamos del punto neutro (2 anomalías)
        confidence = abs(anomaly_count - 2) / 2.0
        
        return round(confidence, 2)
    
    def collect_signals(self, anomaly_signals: Dict) -> List[str]:
        signals = []
        
        if anomaly_signals.get("amount_anomaly", {}).get("is_anomaly"):
            signals.append("monto inusual")
        
        if anomaly_signals.get("time_anomaly", {}).get("is_anomaly"):
            signals.append("horario inusual")
        
        if anomaly_signals.get("device_anomaly", {}).get("is_anomaly"):
            signals.append("dispositivo inusual")
        
        if anomaly_signals.get("country_anomaly", {}).get("is_anomaly"):
            signals.append("país inusual")
        
        if not signals:
            signals.append("transacción normal")
        
        return signals