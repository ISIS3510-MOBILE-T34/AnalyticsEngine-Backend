from firebase_admin import firestore
from typing import List
from models import Transaction, Account
import datetime

class FirestoreService:
    def __init__(self):
        self.db = firestore.client()

    async def get_user_transactions(self, user_id: str) -> List[Transaction]:
        """Obtiene todas las transacciones de todas las cuentas del usuario."""
        transactions = []
        
        # Obtener todas las cuentas del usuario
        accounts_ref = self.db.collection('accounts')
        query = accounts_ref.where('user_id', '==', user_id)
        account_docs = query.stream()

        for account_doc in account_docs:
            # Obtener todas las transacciones de cada cuenta
            transactions_ref = account_doc.reference.collection('transactions')
            transaction_docs = transactions_ref.stream()

            for trans_doc in transaction_docs:
                trans_data = trans_doc.to_dict()
                
                # Convertir la marca de tiempo de Firestore a datetime
                date_time = trans_data.get('dateTime')
                if date_time == firestore.SERVER_TIMESTAMP:
                    date_time = datetime.datetime.now()
                
                # Crear objeto Location si existe
                location = None
                if 'location' in trans_data and trans_data['location']:
                    location = {
                        'latitude': trans_data['location'].get('latitude'),
                        'longitude': trans_data['location'].get('longitude')
                    }

                transaction = Transaction(
                    transaction_id=trans_doc.id,
                    amount=trans_data.get('amount', 0),
                    dateTime=date_time,
                    location=location,
                    transactionName=trans_data.get('transactionName', ''),
                    transactionType=trans_data.get('transactionType', '')
                )
                transactions.append(transaction)

        return sorted(transactions, key=lambda x: x.dateTime)

    async def update_transaction_anomalies(self, user_id: str, transaction_id: str, 
                                        location_anomaly: bool = None, 
                                        amount_anomaly: bool = None) -> bool:
        """Updates the anomaly flags for a transaction."""
        try:
            # Find the transaction in all user accounts
            accounts_ref = self.db.collection('accounts')
            query = accounts_ref.where('user_id', '==', user_id)
            account_docs = query.stream()

            for account_doc in account_docs:
                transaction_ref = account_doc.reference.collection('transactions').document(transaction_id)
                transaction_doc = transaction_ref.get()
                
                if transaction_doc.exists:
                    update_data = {}
                    if location_anomaly is not None:
                        update_data['locationAnomaly'] = location_anomaly
                    if amount_anomaly is not None:
                        update_data['amountAnomaly'] = amount_anomaly
                    
                    if update_data:
                        transaction_ref.update(update_data)
                    return True

            return False
        except Exception as e:
            print(f"Error updating transaction anomalies: {str(e)}")
            return False