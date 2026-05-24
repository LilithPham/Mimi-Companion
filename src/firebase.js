import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyDHLzmdCdWzdXY3Whc04XhOxTaIMy_Ylzs",
  authDomain: "iot-secod-year.firebaseapp.com",
  databaseURL: "https://iot-secod-year-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "iot-secod-year",
  storageBucket: "iot-secod-year.firebasestorage.app",
  messagingSenderId: "780632159514",
  appId: "1:780632159514:web:e876032a9635bb0a8aa8a3",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
