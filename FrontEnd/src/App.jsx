import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Shield } from 'lucide-react';
import TestTransaction from './pages/TestTransaction';
import HITLQueue from './pages/HITLQueue';
import TransactionDetail from './pages/TransactionDetail';
import AllTransactions from './pages/AllTransactions';
import TransactionView from './pages/TransactionView';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white">
        {/* Header */}
        <header className="border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-3">
                <Shield className="w-8 h-8" />
                <h1 className="text-xl font-bold">Fraud Detection System</h1>
              </div>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <nav className="border-b border-gray-200 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8 h-12 items-center">
              <Link
                to="/"
                className="text-sm font-medium hover:text-gray-600 transition-colors"
              >
                Test Transaction
              </Link>
              <Link
                to="/hitl-queue"
                className="text-sm font-medium hover:text-gray-600 transition-colors"
              >
                HITL Queue
              </Link>
              <Link
                to="/transactions"
                className="text-sm font-medium hover:text-gray-600 transition-colors"
              >
                All Transactions
              </Link>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<TestTransaction />} />
            <Route path="/hitl-queue" element={<HITLQueue />} />
            <Route path="/hitl/:transactionId" element={<TransactionDetail />} />
            <Route path="/transactions" element={<AllTransactions />} />
            <Route path="/transaction/:transactionId" element={<TransactionView />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
