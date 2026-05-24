import { db } from "./firebase.js";
import { collection, getDocs } from "firebase/firestore";

const testConnection = async () => {
  console.log("🔄 Đang kiểm tra kết nối Firebase...");
  try {
    const usersRef = collection(db, "users");
    const snapshot = await getDocs(usersRef);
    console.log("✅ Kết nối thành công!");
    console.log("📦 Số users trong collection:", snapshot.size);
  } catch (error) {
    console.error("❌ Lỗi kết nối:", error.message);
  }
};

testConnection();
