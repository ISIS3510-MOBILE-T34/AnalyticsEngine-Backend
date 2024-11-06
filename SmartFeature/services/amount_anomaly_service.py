from typing import List, Tuple
from models import Transaction
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
import logging

logger = logging.getLogger(__name__)

class AmountAnomalyService:
    def __init__(self):
        """
        Initializes the anomaly detection service with the Local Outlier Factor (LOF) model.
        The LOF model detects anomalies by comparing the density of each transaction's amount
        with its neighbors, identifying transactions that significantly deviate in value.
        """
        self.lof = LocalOutlierFactor(
            n_neighbors=5,           # Number of neighbors to use in determining anomaly scores
            contamination=0.1         # Expected fraction of transactions to be anomalous (10%)
        )
        self.MIN_TRANSACTIONS = 5     # Minimum number of transactions needed for analysis

    def detect_amount_anomaly(self, transaction: Transaction, historical_transactions: List[Transaction]) -> Tuple[bool, float, str]:
        """
        Detects anomalies in the transaction amount by analyzing it against similar past transactions.
        Uses the Local Outlier Factor (LOF) model to evaluate whether the transaction amount is unusual.

        Args:
            transaction (Transaction): The transaction to analyze.
            historical_transactions (List[Transaction]): Past transactions for comparison.

        Returns:
            Tuple[bool, float, str]: Indicates if the transaction is anomalous, the confidence level, and a description.
        """
        # If there aren't enough historical transactions, return insufficient data message.
        if len(historical_transactions) < self.MIN_TRANSACTIONS:
            return False, 0.0, f"Insufficient historical data (need at least {self.MIN_TRANSACTIONS} transactions)"

        # Filters past transactions to only those of the same type (Income or Expense) as the new transaction.
        same_type_transactions = [
            t for t in historical_transactions 
            if t.transactionType == transaction.transactionType
        ]

        # If there aren't enough same-type transactions, return insufficient data message for that type.
        if len(same_type_transactions) < self.MIN_TRANSACTIONS:
            return False, 0.0, f"Insufficient transactions of type {transaction.transactionType}"

        # Extracts the amounts from same-type historical transactions to prepare for LOF analysis.
        amounts = np.array([t.amount for t in same_type_transactions])
        current_amount = transaction.amount

        # Adds the amount of the current transaction to the historical amounts for analysis.
        all_amounts = np.append(amounts, current_amount)
        amounts_2d = all_amounts.reshape(-1, 1)  # Reshapes to 2D as required by LOF

        # Applies the LOF model to detect anomalies, catching exceptions in case of errors.
        try:
            # Anomaly scores: -1 indicates anomaly, 1 indicates normal
            lof_scores = self.lof.fit_predict(amounts_2d)
            
            # Checks if the current transaction (last in the array) is marked as an anomaly
            is_anomaly = lof_scores[-1] == -1

            # If an anomaly, calculate the statistics and context for detailed reporting
            if is_anomaly:
                mean_amount = np.mean(amounts)
                median_amount = np.median(amounts)

                # Calculates how many times larger/smaller the current amount is compared to the median
                ratio_to_median = current_amount / median_amount if median_amount > 0 else float('inf')
                
                # Sets a fixed confidence level for simplicity
                confidence = 0.85
                
                # Creates a descriptive detail based on how much the transaction amount deviates from the median
                if ratio_to_median > 1:
                    detail = f"{ratio_to_median:.1f}x larger than median"
                else:
                    detail = f"{(1/ratio_to_median):.1f}x smaller than median"

                # Constructs the reason string with transaction information and deviation details
                reason = (
                    f"Unusual {transaction.transactionType}: ${current_amount:,.2f}\n"
                    f"Typical amount (median): ${median_amount:,.2f}\n"
                    f"Transaction is {detail}"
                )
                
                return True, confidence, reason

            # If not an anomaly, returns normal status
            return False, 0.0, "Transaction amount appears normal"

        except Exception as e:
            # Logs any error encountered during LOF analysis and returns a failure message
            logger.error(f"Error in LOF analysis: {str(e)}")
            return False, 0.0, "Could not perform anomaly analysis"

    def get_transaction_statistics(self, transactions: List[Transaction]) -> dict:
        """
        Calculates basic statistical data for Income and Expense transactions, such as median,
        minimum, maximum, and count for each transaction type.

        Args:
            transactions (List[Transaction]): A list of transactions to analyze.

        Returns:
            dict: A dictionary containing statistical information on income and expense transactions.
        """
        if not transactions:
            return {}  # Returns empty if no transactions provided

        # Splits the transactions into income and expense categories
        income_transactions = [t for t in transactions if t.transactionType == "Income"]
        expense_transactions = [t for t in transactions if t.transactionType == "Expense"]

        # Helper function to compute statistics for a given type of transaction
        def get_stats(transactions, type_name):
            if not transactions:
                return {}  # Returns empty if there are no transactions of the type
                
            # Collects amounts and calculates statistical metrics
            amounts = [t.amount for t in transactions]
            return {
                f"{type_name}_median": float(np.median(amounts)),
                f"{type_name}_min": float(np.min(amounts)),
                f"{type_name}_max": float(np.max(amounts)),
                f"{type_name}_count": len(amounts)
            }

        # Initializes an empty dictionary to hold statistics for both income and expense types
        stats = {}
        stats.update(get_stats(income_transactions, "income"))
        stats.update(get_stats(expense_transactions, "expense"))
        
        return stats  # Returns a dictionary with statistical data for each transaction type
