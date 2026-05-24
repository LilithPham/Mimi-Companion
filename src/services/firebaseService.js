import { db, auth } from "../firebase.js";
import { 
  collection, 
  addDoc, 
  getDocs, 
  getDoc,
  doc, 
  updateDoc, 
  query, 
  where, 
  orderBy 
} from "firebase/firestore";
import { 
  signInWithPopup, 
  GoogleAuthProvider 
} from "firebase/auth";

// ========== ĐĂNG NHẬP ==========
export const loginWithGoogle = async () => {
  const provider = new GoogleAuthProvider();
  try {
    const result = await signInWithPopup(auth, provider);
    const user = result.user;
    
    const userRef = doc(db, "users", user.uid);
    const userSnap = await getDoc(userRef);
    
    if (!userSnap.exists()) {
      await addDoc(collection(db, "users"), {
        uid: user.uid,
        name: user.displayName,
        email: user.email,
        targetBand: null,
        createdAt: new Date()
      });
    }
    return { success: true, user: user };
  } catch (error) {
    console.error("Lỗi đăng nhập:", error);
    return { success: false, error: error.message };
  }
};

// ========== TẠO BUỔI THI MỚI ==========
export const createSession = async (userId, topic) => {
  try {
    const docRef = await addDoc(collection(db, "sessions"), {
      userId: userId,
      topic: topic,
      examDate: new Date(),
      status: "in_progress",
      createdAt: new Date()
    });
    return { success: true, sessionId: docRef.id };
  } catch (error) {
    console.error("Lỗi tạo session:", error);
    return { success: false, error: error.message };
  }
};

// ========== LƯU FEEDBACK ==========
export const saveFeedback = async (sessionId, userId, message, correction, grammarMistake, score) => {
  try {
    await addDoc(collection(db, "feedbacks"), {
      sessionId: sessionId,
      userId: userId,
      role: "user",
      message: message,
      correction: correction,
      grammarMistake: grammarMistake,
      score: score,
      timestamp: new Date()
    });
    return { success: true };
  } catch (error) {
    console.error("Lỗi lưu feedback:", error);
    return { success: false, error: error.message };
  }
};

// ========== KẾT THÚC BÀI THI ==========
export const completeSession = async (sessionId, totalScore) => {
  try {
    const sessionRef = doc(db, "sessions", sessionId);
    await updateDoc(sessionRef, {
      status: "completed",
      totalScore: totalScore,
      completedAt: new Date()
    });
    return { success: true };
  } catch (error) {
    console.error("Lỗi kết thúc session:", error);
    return { success: false, error: error.message };
  }
};

// ========== LẤY LỊCH SỬ HỌC TẬP ==========
export const getUserHistory = async (userId) => {
  try {
    const sessionsQuery = query(
      collection(db, "sessions"),
      where("userId", "==", userId),
      where("status", "==", "completed"),
      orderBy("examDate", "desc")
    );
    const sessionsSnapshot = await getDocs(sessionsQuery);
    const sessions = sessionsSnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    
    const history = await Promise.all(sessions.map(async (session) => {
      const feedbacksQuery = query(
        collection(db, "feedbacks"),
        where("sessionId", "==", session.id),
        orderBy("timestamp", "asc")
      );
      const fbSnapshot = await getDocs(feedbacksQuery);
      const feedbacks = fbSnapshot.docs.map(doc => doc.data());
      
      return {
        session: session,
        chatHistory: feedbacks
      };
    }));
    
    return { success: true, data: history };
  } catch (error) {
    console.error("Lỗi lấy lịch sử:", error);
    return { success: false, error: error.message };
  }
};

// ========== DRAFT (LƯU TẠM) ==========
export const saveDraft = (sessionId, message) => {
  localStorage.setItem(`draft_${sessionId}`, message);
};

export const getDraft = (sessionId) => {
  return localStorage.getItem(`draft_${sessionId}`) || "";
};

export const clearDraft = (sessionId) => {
  localStorage.removeItem(`draft_${sessionId}`);
};
