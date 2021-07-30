importScripts("https://www.gstatic.com/firebasejs/8.7.1/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/8.7.1/firebase-messaging.js");

firebase.initializeApp({
    apiKey: '{{ FIREBASE_API_KEY }}',
    authDomain: '{{ FIREBASE_AUTH_DOMAIN }}',
    projectId: '{{ FIREBASE_PROJECT_ID }}',
    storageBucket: '{{ FIREBASE_STORAGE_BUCKET }}',
    messagingSenderId: '{{ FIREBASE_MESSAGING_SENDER_ID }}',
    appId: '{{ FIREBASE_APP_ID }}',
})

const messaging = firebase.messaging();