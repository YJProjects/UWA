// Import the functions you need from the SDKs you need
import { getApp, getApps, initializeApp, type FirebaseApp } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";

function getFirebaseAuth() : Auth {
  const firebaseConfig = {
    apiKey: "AIzaSyAgz6H6u0WTb7j7nHmZyo6gTkacwzO95m0",
    authDomain: "umdwa-7fa22.firebaseapp.com",
    projectId: "umdwa-7fa22",
    storageBucket: "umdwa-7fa22.firebasestorage.app",
    messagingSenderId: "861208964364",
    appId: "1:861208964364:web:c121e0ffbf9b48070e2d29"
  };

  // Initialize Firebase
  const app : FirebaseApp = getApps().length > 0
    ? getApp()
    : initializeApp(firebaseConfig);
  const auth : Auth = getAuth(app);

  return auth
}

export {
  getFirebaseAuth,
}
