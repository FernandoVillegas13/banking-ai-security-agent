import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
} from 'lucide-react';
import { getHITLTransaction, reviewTransaction } from '../services/api';

const TransactionDetail = () => {
  const { transactionId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [showConfirm, setShowConfirm] = useState(false);
  const [pendingDecision, setPendingDecision] = useState(null);

  useEffect(() => {
    fetchTransaction();
  }, [transactionId]);

  const fetchTransaction = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getHITLTransaction(transactionId);
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

  const handleReview = (decision) => {
    setPendingDecision(decision);
    setShowConfirm(true);
  };

  const confirmReview = async () => {
    setSubmitting(true);
    try {
      await reviewTransaction(transactionId, pendingDecision, reviewNotes);
      navigate('/hitl-queue');
    } catch (err) {
      setError(err.message || 'Error submitting review');
    } finally {
      setSubmitting(false);
      setShowConfirm(false);
    }
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
          onClick={() => navigate('/hitl-queue')}
          className="flex items-center space-x-2 text-gray-600 hover:text-black"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Queue</span>
        </button>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/hitl-queue')}
          className="flex items-center space-x-2 text-gray-600 hover:text-black"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Queue</span>
        </button>
      </div>

      {/* Transaction ID */}
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
            <AlertTriangle className="w-8 h-8" />
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

      {/* Transaction Details */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white border border-gray-200 rounded-lg p-6"
      >
        <h3 className="text-lg font-semibold mb-4">Transaction Details</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
      </motion.div>

      {/* Anomaly Signals */}
      {data.anomaly_signals && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
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
          transition={{ delay: 0.4 }}
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
          transition={{ delay: 0.5 }}
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
          transition={{ delay: 0.6 }}
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
          transition={{ delay: 0.7 }}
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

      {/* Review Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="bg-white border-2 border-black rounded-lg p-6"
      >
        <h3 className="text-lg font-semibold mb-4">Human Review</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Review Notes</label>
            <textarea
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
              rows={4}
              placeholder="Add your review notes here..."
            />
          </div>
          <div className="flex space-x-4">
            <button
              onClick={() => handleReview('APPROVE')}
              disabled={submitting}
              className="flex-1 bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <CheckCircle className="w-5 h-5" />
              <span>Approve Transaction</span>
            </button>
            <button
              onClick={() => handleReview('BLOCK')}
              disabled={submitting}
              className="flex-1 bg-red-600 text-white py-3 rounded-lg font-medium hover:bg-red-700 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <XCircle className="w-5 h-5" />
              <span>Block Transaction</span>
            </button>
          </div>
        </div>
      </motion.div>

      {/* Confirmation Modal */}
      <AnimatePresence>
        {showConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => !submitting && setShowConfirm(false)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-bold mb-4">Confirm Decision</h3>
              <p className="text-gray-700 mb-6">
                Are you sure you want to <strong>{pendingDecision}</strong> this transaction?
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowConfirm(false)}
                  disabled={submitting}
                  className="flex-1 border border-gray-300 py-2 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmReview}
                  disabled={submitting}
                  className={`flex-1 text-white py-2 rounded-lg font-medium flex items-center justify-center space-x-2 disabled:opacity-50 ${
                    pendingDecision === 'APPROVE' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'
                  }`}
                >
                  {submitting ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      <span>Submitting...</span>
                    </>
                  ) : (
                    <span>Confirm</span>
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TransactionDetail;
