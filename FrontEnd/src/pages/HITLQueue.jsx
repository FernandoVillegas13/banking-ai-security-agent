import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Clock, AlertCircle, Loader, RefreshCw } from 'lucide-react';
import { getPendingHITL } from '../services/api';

const HITLQueue = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [queueData, setQueueData] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchQueue = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      const data = await getPendingHITL();
      setQueueData(data);
    } catch (err) {
      setError(err.message || 'Error fetching HITL queue');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleRefresh = () => {
    fetchQueue(true);
  };

  const handleTransactionClick = (transactionId) => {
    navigate(`/hitl/${transactionId}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-2">Human-in-the-Loop Queue</h2>
          <p className="text-gray-600">Transactions requiring human review</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {queueData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Queue Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center space-x-3">
                <Clock className="w-8 h-8 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-600">Queue Length</p>
                  <p className="text-3xl font-bold">{queueData.queue_length || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center space-x-3">
                <AlertCircle className="w-8 h-8 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-600">Pending Reviews</p>
                  <p className="text-3xl font-bold">
                    {queueData.pending_transactions ? queueData.pending_transactions.length : 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                  <span className="text-lg font-bold">%</span>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Escalation Rate</p>
                  <p className="text-3xl font-bold">
                    {queueData.queue_length > 0 ? '100' : '0'}%
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Transaction List */}
          <div className="bg-white border border-gray-200 rounded-lg">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold">Pending Transactions</h3>
            </div>

            {queueData.pending_transactions && queueData.pending_transactions.length > 0 ? (
              <div className="divide-y divide-gray-200">
                {queueData.pending_transactions.map((transactionId, idx) => (
                  <motion.div
                    key={transactionId}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    onClick={() => handleTransactionClick(transactionId)}
                    className="p-6 hover:bg-gray-50 cursor-pointer transition-colors group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                          <AlertCircle className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-semibold text-lg">{transactionId}</p>
                          <p className="text-sm text-gray-600">Awaiting human review</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 text-gray-400 group-hover:text-black transition-colors">
                        <span className="text-sm">Review</span>
                        <svg
                          className="w-5 h-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="p-12 text-center text-gray-400">
                <Clock className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg">No pending transactions</p>
                <p className="text-sm">All transactions have been reviewed</p>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default HITLQueue;
