# AnalyticsEngine (Backend) for SpendiQ
This Repository is used to store documentation about the structure and use the team is giving to the analytics engine instance.

The app's backend analytics engine is being worked with a FireStore Database from Google's Firebase.
![image](https://github.com/user-attachments/assets/d3ce923b-e520-425c-b161-c6f1a7fdf4d2)

## Rationale behind choosing Firebase-Firestore

We chose Firebase (a FireStore Documentary Database instance) as the engine for our Analytics backend, because it provides a no-SQL way of storing and retrieving data, which can lead to a better horizontal scalability of the app without compromising security. Additionally, it is convenient because it is provided with a clear interface, security features, an analytics section to know about the app's usage, crashlytics and, in general, a clear interface to monitor our app in execution and production.

## Analytics Engine Creation Strategy

The team linked each app (Android and iOS) to the Firebase project in order to be able to use the Firebase SDK inside the apps' coding environment like Xcode and Android Studio without any problem.

A FireStore Database instance was created to store data in the shape of Collections and documents, which will allow an easy way to create and retrieve the necessary information to create Knowledge inside the mobile applications.

### 1. List of Created Collections in the Backend

![image](https://github.com/user-attachments/assets/c4372b91-f2b1-4a8c-a6dd-778e6be3c379)

This is the list of collections that were created inside the FireStore instance, each one of them has an example document as a reference. It can be checked with more quality in the route: documentation/collections-list/Collections-inside-Firestore.png

### 2. UML Diagram for Collections and their Dependencies

![image](https://github.com/user-attachments/assets/177a3342-a81d-438a-adb1-88a4187eede2)

This is a UML diagram representation of the collections created and their relations of dependence inside the FireStore instance.

The image can be checked as well in the following route: documentation/backend-diagram/Analytics Engine Diagram.png


