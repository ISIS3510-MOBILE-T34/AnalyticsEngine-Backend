from typing import List, Tuple
from models import Transaction, Location
from geopy.distance import geodesic
import numpy as np
from sklearn.cluster import KMeans

class AnomalyDetectionService:
    def __init__(self):
        """
        Inicializa el servicio de detección de anomalías con parámetros para definir
        condiciones de "normalidad" en términos de distancia y tiempo entre transacciones.
        """
        self.MAX_NORMAL_DISTANCE = 50.0  # Distancia máxima considerada normal en kilómetros
        self.MAX_NORMAL_TIME = 24        # Tiempo máximo considerado normal entre transacciones en horas
        self.MIN_TRANSACTIONS_FOR_CLUSTERING = 5  # Mínimo de transacciones necesarias para hacer clustering

    def detect_anomaly(self, transaction: Transaction, historical_transactions: List[Transaction]) -> Tuple[bool, float, str]:
        """
        Detecta si una transacción es anómala basada en ubicación y tiempo en relación
        con transacciones previas en el historial.

        Args:
            transaction (Transaction): La transacción actual a analizar.
            historical_transactions (List[Transaction]): Historial de transacciones previas para comparación.

        Returns:
            Tuple[bool, float, str]: Indica si es anómala, el nivel de confianza, y una descripción.
        """
        # Verifica si la transacción actual tiene datos de ubicación; si no, no puede hacer análisis de distancia.
        if not transaction.location:
            return False, 0.0, "No location data available"

        # 1. Análisis de distancia y tiempo con la última transacción
        if historical_transactions:
            last_transaction = historical_transactions[-1]  # Obtiene la última transacción en el historial
            if last_transaction.location:
                # Calcula la distancia entre la ubicación de la última y la transacción actual
                distance = self._calculate_distance(transaction.location, last_transaction.location)
                
                # Calcula la diferencia de tiempo en horas entre ambas transacciones
                time_diff = (transaction.dateTime - last_transaction.dateTime).total_seconds() / 3600

                # Si la distancia supera el límite y el tiempo es muy corto, se marca como anómalo
                if distance > self.MAX_NORMAL_DISTANCE:
                    if time_diff < self.MAX_NORMAL_TIME:
                        return True, 0.9, f"Unusual distance ({distance:.1f}km) in short time period ({time_diff:.1f}h)"

        # 2. Análisis de clusters de ubicaciones
        # Crea una lista de coordenadas de ubicación para todas las transacciones con ubicación en el historial.
        locations = [
            (t.location.latitude, t.location.longitude) 
            for t in historical_transactions 
            if t.location
        ]

        # Si hay suficientes transacciones para hacer clustering, se aplica KMeans para identificar áreas comunes.
        if len(locations) >= self.MIN_TRANSACTIONS_FOR_CLUSTERING:
            kmeans = KMeans(n_clusters=min(3, len(locations)), random_state=42)  # Define hasta 3 clusters
            kmeans.fit(locations)  # Agrupa las ubicaciones en clusters
            
            # Convierte la ubicación de la transacción actual en un array compatible con KMeans
            new_location = np.array([[transaction.location.latitude, transaction.location.longitude]])
            
            # Calcula la distancia de la transacción actual a cada centroide de los clusters
            distances_to_clusters = [
                geodesic(
                    (transaction.location.latitude, transaction.location.longitude),
                    (center[0], center[1])
                ).kilometers
                for center in kmeans.cluster_centers_
            ]
            
            # Selecciona la menor distancia entre la ubicación actual y los clusters existentes
            min_distance = min(distances_to_clusters)
            # Si la ubicación de la transacción está demasiado lejos de los clusters conocidos, es anómala
            if min_distance > self.MAX_NORMAL_DISTANCE:
                return True, 0.8, f"Location outside of usual areas (Distance to nearest cluster: {min_distance:.1f}km)"

        # Si no se detectan anomalías, devuelve un resultado indicando normalidad
        return False, 0.0, "Transaction appears normal"

    def _calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """
        Calcula la distancia en kilómetros entre dos ubicaciones.

        Args:
            loc1 (Location): Ubicación 1.
            loc2 (Location): Ubicación 2.

        Returns:
            float: La distancia en kilómetros entre ambas ubicaciones.
        """
        return geodesic(
            (loc1.latitude, loc1.longitude),
            (loc2.latitude, loc2.longitude)
        ).kilometers
