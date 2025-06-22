"""
Crypto Quiz Service for educational blockchain mini-game
"""
import random
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CryptoQuizService:
    """Service for managing crypto/blockchain educational quiz game"""
    
    def __init__(self):
        self.quiz_questions = self._load_quiz_questions()
        self.user_sessions = {}  # Store active quiz sessions
        logger.info("CryptoQuizService initialized")
    
    def _load_quiz_questions(self) -> Dict[str, List[Dict]]:
        """Load quiz questions organized by difficulty level"""
        return {
            "beginner": [
                {
                    "question": "What is Bitcoin?",
                    "options": ["A company", "A digital currency", "A bank", "A website"],
                    "correct": 1,
                    "explanation": "Bitcoin is the first and most well-known cryptocurrency, a digital currency that operates without a central authority."
                },
                {
                    "question": "What is blockchain?",
                    "options": ["A type of database", "A cryptocurrency", "A computer", "A bank account"],
                    "correct": 0,
                    "explanation": "Blockchain is a distributed ledger technology that maintains a continuously growing list of records, called blocks."
                },
                {
                    "question": "Who created Bitcoin?",
                    "options": ["Elon Musk", "Satoshi Nakamoto", "Bill Gates", "Mark Zuckerberg"],
                    "correct": 1,
                    "explanation": "Bitcoin was created by an anonymous person or group using the pseudonym Satoshi Nakamoto."
                },
                {
                    "question": "What does 'HODL' mean in crypto?",
                    "options": ["Hold On for Dear Life", "High Order Data Link", "Hold Original Digital Ledger", "None of these"],
                    "correct": 0,
                    "explanation": "HODL originated from a misspelled 'hold' and became a crypto strategy meaning to hold rather than sell."
                },
                {
                    "question": "What is a cryptocurrency wallet?",
                    "options": ["A physical wallet", "Software to store crypto", "A bank account", "A mining machine"],
                    "correct": 1,
                    "explanation": "A cryptocurrency wallet is software that stores private keys and allows you to send and receive crypto."
                },
                {
                    "question": "What is Ethereum?",
                    "options": ["A type of Bitcoin", "A blockchain platform", "A mining company", "A crypto exchange"],
                    "correct": 1,
                    "explanation": "Ethereum is a blockchain platform that enables smart contracts and decentralized applications (dApps)."
                },
                {
                    "question": "What is crypto mining?",
                    "options": ["Digging for crypto", "Validating transactions", "Buying crypto", "Trading crypto"],
                    "correct": 1,
                    "explanation": "Crypto mining is the process of validating transactions and adding them to the blockchain."
                },
                {
                    "question": "What does DeFi stand for?",
                    "options": ["Digital Finance", "Decentralized Finance", "Distributed Finance", "Direct Finance"],
                    "correct": 1,
                    "explanation": "DeFi stands for Decentralized Finance, referring to financial services built on blockchain."
                }
            ],
            "intermediate": [
                {
                    "question": "What is a smart contract?",
                    "options": ["A legal document", "Self-executing code", "A mining contract", "A trading agreement"],
                    "correct": 1,
                    "explanation": "Smart contracts are self-executing contracts with terms directly written into code."
                },
                {
                    "question": "What consensus mechanism does Bitcoin use?",
                    "options": ["Proof of Stake", "Proof of Work", "Delegated Proof of Stake", "Proof of Authority"],
                    "correct": 1,
                    "explanation": "Bitcoin uses Proof of Work (PoW) consensus mechanism for validating transactions."
                },
                {
                    "question": "What is a 51% attack?",
                    "options": ["High trading volume", "Majority network control", "Price manipulation", "Exchange hack"],
                    "correct": 1,
                    "explanation": "A 51% attack occurs when someone controls more than half of a blockchain network's mining power."
                },
                {
                    "question": "What is the maximum supply of Bitcoin?",
                    "options": ["21 million", "100 million", "1 billion", "Unlimited"],
                    "correct": 0,
                    "explanation": "Bitcoin has a maximum supply cap of 21 million coins, built into its protocol."
                },
                {
                    "question": "What is a hash function in blockchain?",
                    "options": ["Password generator", "Mathematical function", "Mining software", "Wallet address"],
                    "correct": 1,
                    "explanation": "A hash function takes input data and produces a fixed-size string output, crucial for blockchain security."
                },
                {
                    "question": "What is gas in Ethereum?",
                    "options": ["Fuel for cars", "Transaction fee", "Mining reward", "Staking reward"],
                    "correct": 1,
                    "explanation": "Gas is the fee paid to execute transactions and smart contracts on the Ethereum network."
                },
                {
                    "question": "What is a fork in blockchain?",
                    "options": ["Eating utensil", "Protocol change", "Mining tool", "Wallet type"],
                    "correct": 1,
                    "explanation": "A fork is a change to the blockchain protocol rules, creating divergent versions."
                },
                {
                    "question": "What is staking?",
                    "options": ["Gambling", "Locking tokens", "Mining", "Trading"],
                    "correct": 1,
                    "explanation": "Staking involves locking up cryptocurrency to support network operations and earn rewards."
                }
            ],
            "advanced": [
                {
                    "question": "What is the Byzantine Generals Problem?",
                    "options": ["Military strategy", "Consensus challenge", "Trading problem", "Mining difficulty"],
                    "correct": 1,
                    "explanation": "The Byzantine Generals Problem addresses achieving consensus in distributed systems with potentially malicious actors."
                },
                {
                    "question": "What is a Merkle Tree?",
                    "options": ["Tree species", "Data structure", "Mining pool", "Consensus algorithm"],
                    "correct": 1,
                    "explanation": "A Merkle Tree is a binary tree data structure used to efficiently verify data integrity in blockchains."
                },
                {
                    "question": "What is the difference between Layer 1 and Layer 2?",
                    "options": ["Security levels", "Base vs scaling", "Mining vs staking", "Public vs private"],
                    "correct": 1,
                    "explanation": "Layer 1 is the base blockchain, while Layer 2 provides scaling solutions built on top."
                },
                {
                    "question": "What is sharding in blockchain?",
                    "options": ["Breaking chains", "Database partitioning", "Mining technique", "Consensus method"],
                    "correct": 1,
                    "explanation": "Sharding splits the blockchain database into smaller, manageable pieces to improve scalability."
                },
                {
                    "question": "What is a zero-knowledge proof?",
                    "options": ["No proof needed", "Private verification", "Mining proof", "Consensus proof"],
                    "correct": 1,
                    "explanation": "Zero-knowledge proofs allow verification of information without revealing the information itself."
                },
                {
                    "question": "What is the trilemma in blockchain?",
                    "options": ["Three blockchains", "Security/Scalability/Decentralization", "Three consensus", "Three tokens"],
                    "correct": 1,
                    "explanation": "The blockchain trilemma states that blockchains can only achieve two of: security, scalability, and decentralization."
                },
                {
                    "question": "What is an oracle in blockchain?",
                    "options": ["Prediction tool", "External data source", "Mining software", "Consensus node"],
                    "correct": 1,
                    "explanation": "Oracles provide external real-world data to smart contracts on blockchain networks."
                },
                {
                    "question": "What is MEV?",
                    "options": ["Mining Efficiency Value", "Maximum Extractable Value", "Market Exchange Value", "Minimum Entry Value"],
                    "correct": 1,
                    "explanation": "MEV (Maximum Extractable Value) refers to profit extracted by reordering transactions in a block."
                }
            ]
        }
    
    def start_quiz(self, user_id: str, difficulty: str = "beginner") -> Dict:
        """Start a new quiz session for a user"""
        if difficulty not in self.quiz_questions:
            difficulty = "beginner"
        
        questions = random.sample(self.quiz_questions[difficulty], min(5, len(self.quiz_questions[difficulty])))
        
        session = {
            "user_id": user_id,
            "difficulty": difficulty,
            "questions": questions,
            "current_question": 0,
            "score": 0,
            "answers": [],
            "start_time": datetime.now(),
            "status": "active"
        }
        
        self.user_sessions[user_id] = session
        logger.info(f"Started {difficulty} quiz for user {user_id}")
        
        return self.get_current_question(user_id)
    
    def get_current_question(self, user_id: str) -> Optional[Dict]:
        """Get current question for user's active session"""
        if user_id not in self.user_sessions:
            return None
        
        session = self.user_sessions[user_id]
        if session["status"] != "active":
            return None
        
        if session["current_question"] >= len(session["questions"]):
            return self.finish_quiz(user_id)
        
        question = session["questions"][session["current_question"]]
        return {
            "question_number": session["current_question"] + 1,
            "total_questions": len(session["questions"]),
            "question": question["question"],
            "options": question["options"],
            "difficulty": session["difficulty"]
        }
    
    def submit_answer(self, user_id: str, answer_index: int) -> Dict:
        """Submit answer for current question"""
        if user_id not in self.user_sessions:
            return {"error": "No active quiz session"}
        
        session = self.user_sessions[user_id]
        if session["status"] != "active":
            return {"error": "Quiz session not active"}
        
        if session["current_question"] >= len(session["questions"]):
            return {"error": "Quiz already completed"}
        
        current_q = session["questions"][session["current_question"]]
        is_correct = answer_index == current_q["correct"]
        
        if is_correct:
            session["score"] += 1
        
        session["answers"].append({
            "question_index": session["current_question"],
            "user_answer": answer_index,
            "correct_answer": current_q["correct"],
            "is_correct": is_correct
        })
        
        result = {
            "is_correct": is_correct,
            "correct_answer": current_q["options"][current_q["correct"]],
            "explanation": current_q["explanation"],
            "score": session["score"],
            "question_number": session["current_question"] + 1,
            "total_questions": len(session["questions"])
        }
        
        session["current_question"] += 1
        
        # Check if quiz is completed
        if session["current_question"] >= len(session["questions"]):
            result["quiz_completed"] = True
            result["final_results"] = self.finish_quiz(user_id)
        
        return result
    
    def finish_quiz(self, user_id: str) -> Dict:
        """Finish quiz and return final results"""
        if user_id not in self.user_sessions:
            return {"error": "No quiz session found"}
        
        session = self.user_sessions[user_id]
        session["status"] = "completed"
        session["end_time"] = datetime.now()
        
        total_questions = len(session["questions"])
        score = session["score"]
        percentage = (score / total_questions) * 100
        
        # Determine performance level
        if percentage >= 80:
            performance = "Excellent! 🏆"
            message = "You're a blockchain expert!"
        elif percentage >= 60:
            performance = "Good! 👍"
            message = "You have solid blockchain knowledge!"
        elif percentage >= 40:
            performance = "Not bad! 📚"
            message = "Keep learning about blockchain!"
        else:
            performance = "Keep studying! 💪"
            message = "Practice makes perfect!"
        
        results = {
            "score": score,
            "total_questions": total_questions,
            "percentage": percentage,
            "performance": performance,
            "message": message,
            "difficulty": session["difficulty"],
            "duration": (session["end_time"] - session["start_time"]).seconds
        }
        
        logger.info(f"User {user_id} completed {session['difficulty']} quiz: {score}/{total_questions}")
        return results
    
    def get_leaderboard(self, difficulty: str = "all") -> List[Dict]:
        """Get quiz leaderboard (mock implementation for demo)"""
        # In a real implementation, this would query a database
        mock_leaderboard = [
            {"username": "CryptoMaster", "score": 5, "difficulty": "advanced", "percentage": 100},
            {"username": "BlockchainPro", "score": 4, "difficulty": "intermediate", "percentage": 80},
            {"username": "SatoshiFan", "score": 4, "difficulty": "beginner", "percentage": 80},
            {"username": "DeFiLover", "score": 3, "difficulty": "intermediate", "percentage": 60},
            {"username": "HODLer", "score": 3, "difficulty": "beginner", "percentage": 60}
        ]
        
        if difficulty != "all":
            mock_leaderboard = [entry for entry in mock_leaderboard if entry["difficulty"] == difficulty]
        
        return mock_leaderboard[:10]  # Top 10
    
    def get_quiz_stats(self, user_id: str) -> Dict:
        """Get user's quiz statistics"""
        # In a real implementation, this would query a database
        return {
            "total_quizzes": 3,
            "average_score": 75.0,
            "best_score": 100,
            "favorite_difficulty": "intermediate",
            "total_questions_answered": 15,
            "accuracy": 75.0
        }
    
    def has_active_session(self, user_id: str) -> bool:
        """Check if user has an active quiz session"""
        return (user_id in self.user_sessions and 
                self.user_sessions[user_id]["status"] == "active")
    
    def end_session(self, user_id: str) -> bool:
        """End current quiz session"""
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["status"] = "ended"
            return True
        return False