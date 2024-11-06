from fastapi import FastAPI, HTTPException
from models import Transaction, AnomalyResponse, AmountAnomalyResponse, TransactionStatistics
from services.firestore_service import FirestoreService
from services.location_anomaly_service import AnomalyDetectionService
from services.amount_anomaly_service import AmountAnomalyService
from config import FirebaseConfig
import logging
from pydantic import BaseModel

class CombinedAnomalyResponse(BaseModel):
    location_analysis: AnomalyResponse
    amount_analysis: AmountAnomalyResponse
    success: bool

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Firebase
firebase_config = FirebaseConfig()

@app.post("/api/analyze-transaction-location/{user_id}/{transaction_id}", response_model=AnomalyResponse)
async def analyze_transaction(user_id: str, transaction_id: str):
    """Analiza una transacción específica para detectar anomalías geográficas."""
    try:
        firestore_service = FirestoreService()
        anomaly_service = AnomalyDetectionService()

        historical_transactions = await firestore_service.get_user_transactions(user_id)
        current_transaction = next(
            (t for t in historical_transactions if t.transaction_id == transaction_id),
            None
        )
        
        if not current_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        previous_transactions = [
            t for t in historical_transactions 
            if t.dateTime < current_transaction.dateTime
        ]

        is_anomaly, confidence, reason = anomaly_service.detect_anomaly(
            current_transaction,
            previous_transactions
        )

        # Update the locationAnomaly flag in Firebase
        await firestore_service.update_transaction_anomalies(
            user_id, 
            transaction_id, 
            location_anomaly=is_anomaly
        )

        return AnomalyResponse(
            is_anomaly=is_anomaly,
            confidence=confidence,
            reason=reason,
            transaction_id=transaction_id
        )

    except Exception as e:
        logger.error(f"Error analyzing transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-transaction-amount/{user_id}/{transaction_id}", response_model=AmountAnomalyResponse)
async def analyze_transaction_amount(user_id: str, transaction_id: str):
    """Analiza una transacción específica para detectar anomalías en el monto."""
    try:
        firestore_service = FirestoreService()
        amount_anomaly_service = AmountAnomalyService()

        historical_transactions = await firestore_service.get_user_transactions(user_id)
        current_transaction = next(
            (t for t in historical_transactions if t.transaction_id == transaction_id),
            None
        )
        
        if not current_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        previous_transactions = [
            t for t in historical_transactions 
            if t.dateTime < current_transaction.dateTime
        ]

        is_anomaly, confidence, reason = amount_anomaly_service.detect_amount_anomaly(
            current_transaction,
            previous_transactions
        )

        stats = amount_anomaly_service.get_transaction_statistics(previous_transactions)
        statistics = TransactionStatistics(**stats) if stats else None

        # Update the amountAnomaly flag in Firebase
        await firestore_service.update_transaction_anomalies(
            user_id, 
            transaction_id, 
            amount_anomaly=is_anomaly
        )

        return AmountAnomalyResponse(
            is_anomaly=is_anomaly,
            confidence=confidence,
            reason=reason,
            transaction_id=transaction_id,
            statistics=statistics
        )

    except Exception as e:
        logger.error(f"Error analyzing transaction amount: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-transaction-complete/{user_id}/{transaction_id}", response_model=CombinedAnomalyResponse)
async def analyze_transaction_complete(user_id: str, transaction_id: str):
    """Analiza una transacción para detectar anomalías tanto en ubicación como en monto."""
    try:
        firestore_service = FirestoreService()
        anomaly_service = AnomalyDetectionService()
        amount_anomaly_service = AmountAnomalyService()

        historical_transactions = await firestore_service.get_user_transactions(user_id)
        current_transaction = next(
            (t for t in historical_transactions if t.transaction_id == transaction_id),
            None
        )
        
        if not current_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        previous_transactions = [
            t for t in historical_transactions 
            if t.dateTime < current_transaction.dateTime
        ]

        # Location anomaly analysis
        is_location_anomaly, location_confidence, location_reason = anomaly_service.detect_anomaly(
            current_transaction,
            previous_transactions
        )

        # amount anomaly analysis
        is_amount_anomaly, amount_confidence, amount_reason = amount_anomaly_service.detect_amount_anomaly(
            current_transaction,
            previous_transactions
        )

        stats = amount_anomaly_service.get_transaction_statistics(previous_transactions)
        statistics = TransactionStatistics(**stats) if stats else None

        # Update both flags in Firebase
        update_success = await firestore_service.update_transaction_anomalies(
            user_id,
            transaction_id,
            location_anomaly=is_location_anomaly,
            amount_anomaly=is_amount_anomaly
        )

        return CombinedAnomalyResponse(
            location_analysis=AnomalyResponse(
                is_anomaly=is_location_anomaly,
                confidence=location_confidence,
                reason=location_reason,
                transaction_id=transaction_id
            ),
            amount_analysis=AmountAnomalyResponse(
                is_anomaly=is_amount_anomaly,
                confidence=amount_confidence,
                reason=amount_reason,
                transaction_id=transaction_id,
                statistics=statistics
            ),
            success=update_success
        )

    except Exception as e:
        logger.error(f"Error in complete transaction analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
