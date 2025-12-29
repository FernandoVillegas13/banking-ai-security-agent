import { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, CheckCircle, XCircle, Loader } from 'lucide-react';
import { analyzeTransaction } from '../services/api';

const TestTransaction = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const defaultPayload = {
    transaction_id: 'T-1006',
    customer_id: 'CU-001',
    amount: 1000.0,
    currency: 'PEN',
    country: 'PE',
    channel: 'web',
    device_id: 'D-01',
    timestamp: new Date().toISOString().slice(0, 19),
  };

  const [payload, setPayload] = useState(JSON.stringify(defaultPayload, null, 2));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = JSON.parse(payload);
      const response = await analyzeTransaction(data);
      setResult(response);
    } catch (err) {
      setError(err.message || 'Error analyzing transaction');
    } finally {
      setLoading(false);
    }
  };

  const getDecisionIcon = (decision) => {
    switch (decision) {
      case 'APPROVE':
        return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'BLOCK':
        return <XCircle className="w-6 h-6 text-red-600" />;
      case 'CHALLENGE':
        return <div className="w-6 h-6 border-2 border-yellow-600 rounded-full" />;
      case 'ESCALATE_TO_HUMAN':
        return <div className="w-6 h-6 border-2 border-blue-600 rounded-full flex items-center justify-center text-xs">H</div>;
      default:
        return null;
    }
  };

  const getDecisionColor = (decision) => {
    switch (decision) {
      case 'APPROVE':
        return 'bg-green-50 border-green-200';
      case 'BLOCK':
        return 'bg-red-50 border-red-200';
      case 'CHALLENGE':
        return 'bg-yellow-50 border-yellow-200';
      case 'ESCALATE_TO_HUMAN':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Test Transaction</h2>
        <p className="text-gray-600">Send a test transaction to the fraud detection system</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4">Transaction Payload</h3>
          <form onSubmit={handleSubmit}>
            <textarea
              value={payload}
              onChange={(e) => setPayload(e.target.value)}
              className="w-full h-96 p-4 font-mono text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
              placeholder="Enter transaction JSON"
            />
            <button
              type="submit"
              disabled={loading}
              className="mt-4 w-full bg-black text-white py-3 rounded-lg font-medium hover:bg-gray-800 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  <span>Analyze Transaction</span>
                </>
              )}
            </button>
          </form>
        </motion.div>

        {/* Result Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4">Analysis Result</h3>
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Decision */}
              {result.decision && (
                <div className={`border rounded-lg p-4 ${getDecisionColor(result.decision.value)}`}>
                  <div className="flex items-center space-x-3 mb-2">
                    {getDecisionIcon(result.decision.value)}
                    <span className="font-bold text-lg">{result.decision.value}</span>
                  </div>
                  <div className="text-sm text-gray-700">
                    <p className="mb-2"><strong>Confidence:</strong> {(result.decision.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Reasoning:</strong> {result.decision.chain_of_thought}</p>
                  </div>
                </div>
              )}

              {/* Signals */}
              {result.signals && result.signals.length > 0 && (
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Signals Detected</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.signals.map((signal, idx) => (
                      <span key={idx} className="px-3 py-1 bg-gray-100 rounded-full text-sm">
                        {signal}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Explanations */}
              {result.explanations && (
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Customer Explanation</h4>
                  <p className="text-sm text-gray-700">{result.explanations}</p>
                </div>
              )}

              {/* Human Review Required */}
              {result.need_human_review && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-blue-800 font-medium">⚠️ This transaction requires human review</p>
                </div>
              )}

              {/* Full JSON */}
              <details className="border border-gray-200 rounded-lg">
                <summary className="p-4 cursor-pointer font-medium hover:bg-gray-50">
                  View Full Response
                </summary>
                <pre className="p-4 text-xs overflow-auto max-h-96 bg-gray-50 scrollbar-thin">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </details>
            </div>
          )}

          {!result && !error && (
            <div className="flex items-center justify-center h-96 text-gray-400">
              <p>No results yet. Submit a transaction to see the analysis.</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default TestTransaction;
