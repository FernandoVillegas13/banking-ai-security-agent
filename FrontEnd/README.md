# Fraud Detection System - Frontend

A minimalistic black and white React frontend for the multi-agent fraud detection system.

## Features

- **Test Transaction**: Send test transactions to the fraud detection system
- **HITL Queue**: View and manage transactions requiring human review
- **Transaction Details**: Detailed view with all agent analysis, anomaly signals, and evidence
- **All Transactions**: Complete transaction history with filtering

## Tech Stack

- React 18
- Vite
- React Router
- Tailwind CSS
- Framer Motion (animations)
- Lucide React (icons)
- Axios

## Installation

```bash
npm install
```

## Configuration

The frontend is configured to proxy API requests to the backend at `http://localhost:8000`. 

If your backend runs on a different port, update the proxy configuration in `vite.config.js`.

## Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build

Build for production:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## API Endpoints

The frontend connects to these backend endpoints:

- `POST /analize` - Analyze a transaction
- `GET /hitl/pending` - Get pending HITL transactions
- `GET /hitl/{transaction_id}` - Get transaction details
- `POST /hitl/{transaction_id}/review` - Review transaction (APPROVE/BLOCK)
- `GET /transaction/{transaction_id}` - Get single transaction
- `GET /transactions` - Get all transactions

## Project Structure

```
src/
├── services/
│   └── api.js              # API service layer
├── pages/
│   ├── TestTransaction.jsx # Test transaction submission
│   ├── HITLQueue.jsx       # HITL queue view
│   ├── TransactionDetail.jsx # Detailed transaction review
│   └── AllTransactions.jsx # Transaction history
├── App.jsx                 # Main app with routing
├── main.jsx               # Entry point
└── index.css              # Global styles
```

## Usage

### Testing Transactions

1. Navigate to "Test Transaction"
2. Edit the JSON payload (or use the default)
3. Click "Analyze Transaction"
4. View the analysis results

### Reviewing Transactions

1. Navigate to "HITL Queue"
2. Click on a pending transaction
3. Review all the details, signals, and evidence
4. Add review notes (optional)
5. Click "Approve" or "Block"

### Viewing All Transactions

1. Navigate to "All Transactions"
2. Use the dropdown to change the number of items displayed
3. View transaction history with decisions and statuses
