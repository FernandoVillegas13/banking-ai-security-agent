import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Loader,
  AlertTriangle,
  Globe,
  CreditCard,
  Clock,
  Smartphone,
  DollarSign,
  Shield,
  TrendingUp,
  Search,
  MessageSquare,
  User,
  Activity,
  Zap,
} from 'lucide-react';
import { getTransaction } from '../services/api';

const TransactionView = () => {
  const { transactionId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTransaction();
  }, [transactionId]);

  const fetchTransaction = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getTransaction(transactionId);
      if (response.status === 'success') {
        setData(response.data);
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError(err.message || 'Error fetching transaction');
    } finally {
      setLoading(false);
    }
  };

  const getDecisionColor = (decision) => {
    switch (decision) {
      case 'APPROVE':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'BLOCK':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'CHALLENGE':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'ESCALATE_TO_HUMAN':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getDecisionIcon = (decision) => {
    switch (decision) {
      case 'APPROVE':
        return <CheckCircle className="w-8 h-8" />;
      case 'BLOCK':
        return <XCircle className="w-8 h-8" />;
      case 'CHALLENGE':
        return <AlertTriangle className="w-8 h-8" />;
      case 'ESCALATE_TO_HUMAN':
        return <AlertTriangle className="w-8 h-8" />;
      default:
        return <Shield className="w-8 h-8" />;
    }
  };

  const getAgentIcon = (agentName) => {
    const icons = {
      transaction_context_agent: <Activity className="w-5 h-5" />,
      behavioral_agent: <TrendingUp className="w-5 h-5" />,
      internal_policy_rag_agent: <Search className="w-5 h-5" />,
      external_threat_agent: <Globe className="w-5 h-5" />,
      debate_agents: <MessageSquare className="w-5 h-5" />,
      decision_arbiter: <Shield className="w-5 h-5" />,
      explainability_agent: <Zap className="w-5 h-5" />,
      human_review: <User className="w-5 h-5" />,
    };
    return icons[agentName] || <Activity className="w-5 h-5" />;
  };

  const formatAgentName = (name) => {
    if (!name) return 'Unknown Agent';
    return name
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate('/transactions')}
          className="flex items-center space-x-2 text-gray-600 hover:text-black"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Transactions</span>
        </button>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/transactions')}
          className="flex items-center space-x-2 text-gray-600 hover:text-black"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Transactions</span>
        </button>
      </div>

      {/* Transaction ID Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white border border-gray-200 rounded-lg p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">Transaction ID</p>
            <h1 className="text-3xl font-bold">{data.transaction_id}</h1>
          </div>
          <Shield className="w-12 h-12 text-gray-300" />
        </div>
      </motion.div>

      {/* Decision Summary */}
      {data.decision && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={`border rounded-lg p-6 ${getDecisionColor(data.decision.value)}`}
        >
          <div className="flex items-center space-x-3 mb-3">
            {getDecisionIcon(data.decision.value)}
            <h2 className="text-2xl font-bold">{data.decision.value}</h2>
          </div>
          <div className="space-y-2">
            <p className="text-sm">
              <strong>Confidence:</strong> {(data.decision.confidence * 100).toFixed(1)}%
            </p>
            <p className="text-sm">
              <strong>Reasoning:</strong> {data.decision.chain_of_thought}
            </p>
          </div>
        </motion.div>
      )}

      {/* Transaction Details Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
      >
        {/* Transaction Info */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Transaction Details</h3>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <DollarSign className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm text-gray-600">Amount</p>
                <p className="font-semibold">
                  {data.transaction_request.currency} {data.transaction_request.amount.toFixed(2)}
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Globe className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm text-gray-600">Country</p>
                <p className="font-semibold">{data.transaction_request.country}</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Smartphone className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm text-gray-600">Device</p>
                <p className="font-semibold">{data.transaction_request.device_id}</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <CreditCard className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm text-gray-600">Channel</p>
                <p className="font-semibold">{data.transaction_request.channel}</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <User className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm text-gray-600">Customer</p>
                <p className="font-semibold">{data.transaction_request.customer_id}</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Clock className="w-5 h-5 text-gray-400 mt-1" />
              <div>
                <p className="text-sm text-gray-600">Timestamp</p>
                <p className="font-semibold text-xs">
                  {new Date(data.transaction_request.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Usual Behavior */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Usual Behavior</h3>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">Average Amount</p>
              <p className="font-semibold">{data.usual_behavior.usual_amount_avg.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Usual Hours</p>
              <p className="font-semibold">{data.usual_behavior.usual_hours}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Usual Countries</p>
              <p className="font-semibold">{data.usual_behavior.usual_countries}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Usual Devices</p>
              <p className="font-semibold">{data.usual_behavior.usual_devices}</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Agent Timeline */}
      {data.agent_audit && data.agent_audit.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-6 flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>Agent Execution Timeline</span>
          </h3>
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>
            
            {/* Timeline items */}
            <div className="space-y-6">
              {data.agent_audit.map((agent, idx) => {
                if (!agent || !agent.agent_name) return null;
                return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + idx * 0.1 }}
                  className="relative pl-14"
                >
                  {/* Timeline dot */}
                  <div className="absolute left-3 top-1 w-6 h-6 bg-white border-2 border-black rounded-full flex items-center justify-center">
                    {getAgentIcon(agent.agent_name)}
                  </div>
                  
                  {/* Content */}
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold">{formatAgentName(agent.agent_name)}</h4>
                      <span className="text-xs text-gray-600">
                        {formatTime(agent.execution_time)}
                      </span>
                    </div>
                    
                    <div className="space-y-1 text-sm text-gray-700">
                      {agent.anomaly_score !== undefined && (
                        <p><strong>Anomaly Score:</strong> {agent.anomaly_score.toFixed(2)}</p>
                      )}
                      {agent.deviation_score !== undefined && (
                        <p><strong>Deviation Score:</strong> {agent.deviation_score.toFixed(2)}</p>
                      )}
                      {agent.search_query && (
                        <p><strong>Query:</strong> {agent.search_query}</p>
                      )}
                      {agent.query_used && (
                        <p><strong>Query:</strong> {agent.query_used}</p>
                      )}
                      {agent.rounds !== undefined && (
                        <p><strong>Rounds:</strong> {agent.rounds}</p>
                      )}
                      {agent.decision && (
                        <p><strong>Decision:</strong> {agent.decision}</p>
                      )}
                      {agent.duration_seconds !== undefined && (
                        <p><strong>Duration:</strong> {agent.duration_seconds.toFixed(2)}s</p>
                      )}
                      {agent.explanations_generated !== undefined && (
                        <p><strong>Explanations Generated:</strong> {agent.explanations_generated}</p>
                      )}
                      {agent.reviewer_notes && (
                        <p><strong>Notes:</strong> {agent.reviewer_notes}</p>
                      )}
                    </div>
                  </div>
                </motion.div>
                );
              })}
            </div>
          </div>
        </motion.div>
      )}

      {/* Anomaly Signals */}
      {data.anomaly_signals && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5" />
            <span>Anomaly Signals</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(data.anomaly_signals).map(([key, signal]) => (
              <div
                key={key}
                className={`border rounded-lg p-4 ${
                  signal.is_anomaly ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold capitalize">
                    {key.replace('_anomaly', '').replace('_', ' ')}
                  </span>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      signal.is_anomaly ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                    }`}
                  >
                    {(signal.score * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-sm text-gray-700">{signal.reason}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Behavioral Analysis */}
      {data.behavioral_analysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Behavioral Analysis</span>
          </h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600 mb-1">Pattern Deviation</p>
              <p className="text-sm">{data.behavioral_analysis.pattern_deviation}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Deviation Score</p>
              <div className="flex items-center space-x-3">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-black h-2 rounded-full"
                    style={{ width: `${data.behavioral_analysis.deviation_score * 100}%` }}
                  />
                </div>
                <span className="text-sm font-semibold">
                  {(data.behavioral_analysis.deviation_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* RAG Evidence */}
      {data.rag_evidence && data.rag_evidence.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <Search className="w-5 h-5" />
            <span>Internal Policy Evidence</span>
          </h3>
          <div className="space-y-3">
            {data.rag_evidence.map((evidence, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <span className="font-semibold text-sm">{evidence.policy_id}</span>
                  <span className="text-xs text-gray-600">
                    Similarity: {(evidence.similarity_score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-1">{evidence.rule}</p>
                <p className="text-xs text-gray-500">Version: {evidence.version}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* External Threat Evidence */}
      {data.search_evidence && data.search_evidence.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <Globe className="w-5 h-5" />
            <span>External Threat Intelligence</span>
          </h3>
          <div className="space-y-3">
            {data.search_evidence.map((evidence, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4">
                <p className="font-semibold text-sm mb-2">{evidence.fraud_type}</p>
                <p className="text-sm text-gray-700 mb-2">{evidence.summary}</p>
                <a
                  href={evidence.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:underline break-all"
                >
                  {evidence.url}
                </a>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Debate */}
      {data.debate && data.debate.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <MessageSquare className="w-5 h-5" />
            <span>Agent Debate</span>
          </h3>
          <div className="space-y-4">
            {data.debate.map((entry, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg ${
                  entry.agent === 'pro_fraud'
                    ? 'bg-red-50 border border-red-200'
                    : 'bg-green-50 border border-green-200'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold capitalize">
                    {entry.agent.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-gray-600">Round {entry.round}</span>
                </div>
                <p className="text-sm">{entry.argument}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Customer Explanation */}
      {data.explanations && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="bg-white border-2 border-black rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4">Customer Explanation</h3>
          <p className="text-sm text-gray-700 whitespace-pre-line">{data.explanations}</p>
        </motion.div>
      )}
    </div>
  );
};

export default TransactionView;
