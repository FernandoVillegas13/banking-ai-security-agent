import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Loader, RefreshCw, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { getAllTransactions } from '../services/api';

const AllTransactions = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState(null);
  const [limit, setLimit] = useState(50);

  const fetchTransactions = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      const data = await getAllTransactions(limit);
      if (data.status === 'success') {
        setTransactions(data.data || []);
      }
    } catch (err) {
      setError(err.message || 'Error fetching transactions');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [limit]);

  const getDecisionIcon = (decision) => {
    const value = decision?.value || decision;
    switch (value) {
      case 'APPROVE':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'BLOCK':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'CHALLENGE':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'ESCALATE_TO_HUMAN':
        return <AlertCircle className="w-5 h-5 text-blue-600" />;
      default:
        return <div className="w-5 h-5 border-2 border-gray-400 rounded-full" />;
    }
  };

  const getDecisionColor = (decision) => {
    const value = decision?.value || decision;
    switch (value) {
      case 'APPROVE':
        return 'bg-green-50 text-green-700';
      case 'BLOCK':
        return 'bg-red-50 text-red-700';
      case 'CHALLENGE':
        return 'bg-yellow-50 text-yellow-700';
      case 'ESCALATE_TO_HUMAN':
        return 'bg-blue-50 text-blue-700';
      default:
        return 'bg-gray-50 text-gray-700';
    }
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
          <h2 className="text-2xl font-bold mb-2">All Transactions</h2>
          <p className="text-gray-600">Complete transaction history</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
          >
            <option value={10}>10 items</option>
            <option value={25}>25 items</option>
            <option value={50}>50 items</option>
            <option value={100}>100 items</option>
          </select>
          <button
            onClick={() => fetchTransactions(true)}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {transactions.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white border border-gray-200 rounded-lg overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Transaction ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Country
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Decision
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Human Review
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Final Decision
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {transactions.map((transaction, idx) => (
                  <motion.tr
                    key={transaction.transaction_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.02 }}
                    onClick={() => navigate(`/transaction/${transaction.transaction_id}`)}
                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="font-medium">{transaction.transaction_id}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {transaction.transaction_request?.customer_id || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {transaction.transaction_request?.country || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        {getDecisionIcon(transaction.decision)}
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${getDecisionColor(
                            transaction.decision
                          )}`}
                        >
                          {transaction.decision?.value || transaction.decision || 'N/A'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {transaction.decision?.confidence
                        ? `${(transaction.decision.confidence * 100).toFixed(1)}%`
                        : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {transaction.saved_at
                        ? new Date(transaction.saved_at).toLocaleDateString()
                        : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {transaction.reviewed_by_human ? (
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                          Reviewed
                        </span>
                      ) : transaction.need_human_review ? (
                        <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs font-medium">
                          Pending
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                          N/A
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {transaction.last_decision && transaction.reviewed_by_human ? (
                        <div className="flex items-center space-x-2">
                          {getDecisionIcon(transaction.last_decision.value)}
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${getDecisionColor(
                              transaction.last_decision.value
                            )}`}
                          >
                            {transaction.last_decision.value}
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-400 text-xs">—</span>
                      )}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {transactions.length === 0 && !loading && (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-400 text-lg">No transactions found</p>
        </div>
      )}
    </div>
  );
};

export default AllTransactions;
