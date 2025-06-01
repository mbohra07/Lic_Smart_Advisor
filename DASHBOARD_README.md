# 🏛️ LIC Policy Recommendation Dashboard

## Production-Ready Streamlit Dashboard with AI-Powered Sales Agent

A comprehensive, production-ready Streamlit dashboard that integrates with MongoDB Atlas vector database and provides AI-powered LIC policy recommendations with a genius sales agent powered by Groq LLM.

---

## 🌟 **Key Features**

### 🎯 **Intelligent User Profile Collection**
- **Psychologically-optimized multi-step form** with smart defaults
- **Dynamic life stage indicators** based on age (Early Career, Growth Phase, etc.)
- **Real-time income bracket classification** with affordability indicators
- **Interactive risk-return charts** with visual policy alignment
- **Behavioral psychology integration** for decision-making styles
- **Timeline-based urgency creation** with personalized incentives

### 🤖 **Advanced RAG Recommendation Engine**
- **MongoDB Atlas Vector Search integration** with your existing 37+ policies
- **Semantic similarity matching** with 0.6-0.8 similarity thresholds
- **Multi-factor analysis** (demographics, goals, risk tolerance, life stage)
- **Real-time confidence scoring** with detailed match explanations
- **Premium calculations** based on age, income, and policy type
- **Affordability analysis** with income-to-premium ratio optimization

### 🧠 **World's Genius LIC Sales Agent (Groq-Powered)**
- **25+ years simulated experience** with 10,000+ families helped
- **Complete mastery of all 37+ LIC policies** with instant calculations
- **Cultural adaptation** with Hindi phrases and Indian family values
- **Advanced objection handling** with psychological persuasion techniques
- **Personalized sales pitches** generated after recommendations
- **Real-time chat interface** with typing indicators and engagement tracking

### 💬 **Interactive Chat System**
- **Professional agent avatar** with credentials and success metrics
- **Real-time conversation** with intelligent response generation
- **Quick action buttons** (Premium Calculator, Policy Comparison, Tax Benefits)
- **Objection detection and handling** with specialized responses
- **Conversation analytics** with engagement scoring and lead qualification

### 📊 **Comprehensive Analytics Dashboard**
- **Session tracking** with MongoDB chat history persistence
- **Lead scoring algorithm** with conversion probability analysis
- **Engagement metrics** (duration, message count, sentiment analysis)
- **Performance dashboards** with policy comparison charts
- **User behavior insights** with demographic preference analysis

---

## 🏗️ **Architecture Overview**

```
LIC Dashboard Architecture
├── 📱 Frontend (Streamlit)
│   ├── Multi-step Profile Collection
│   ├── AI Recommendation Display
│   ├── Interactive Chat Interface
│   └── Analytics Dashboard
├── 🧠 AI/ML Layer
│   ├── MongoDB Atlas Vector Search
│   ├── Groq LLM Integration
│   ├── RAG Query Engine
│   └── Sales Agent AI
├── 🗄️ Data Layer
│   ├── MongoDB Atlas (Policies)
│   ├── Chat History Collection
│   ├── Session Analytics
│   └── User Profiles
└── 🔧 Infrastructure
    ├── Streamlit Cloud/Server
    ├── Environment Management
    ├── API Key Security
    └── Performance Monitoring
```

---

## 🚀 **Quick Start Guide**

### 1. **Environment Setup**

```bash
# Clone the repository
cd /Users/madhurambohra/Desktop/Lic_advisor_agent_v2

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your_groq_api_key_here"
export GOOGLE_API_KEY="your_google_api_key_here"  # Optional
export GOOGLE_CSE_ID="your_google_cse_id_here"    # Optional
```

### 2. **Database Verification**

```bash
# Verify your MongoDB Atlas vector database
python verify_vector_search.py

# Test RAG recommendations
python rag_recommendation_demo.py
```

### 3. **Launch Dashboard**

```bash
# Run the Streamlit dashboard
streamlit run streamlit_dashboard.py

# Access at: http://localhost:8501
```

---

## 📋 **Dashboard Flow**

### **Page 1: Profile Collection** 👤
1. **Demographics** (Age slider with life stage indicators, Income with bracket classification)
2. **Life Context** (Life stage selection, Dependents, Financial goals with ROI projections)
3. **Financial Psychology** (Risk comfort with visual charts, Decision-making style)
4. **Timeline** (Purchase urgency with timeline-specific incentives)
5. **Summary** (Profile review with dynamic CTA button)

### **Page 2: AI Recommendations** 🎯
1. **Personalized Header** with analysis summary
2. **Primary Recommendation** (Hero card with confidence gauge)
3. **Alternative Options** (3-4 secondary recommendations)
4. **AI Sales Pitch** (Groq-generated personalized presentation)

### **Page 3: Expert Chat** 💬
1. **Agent Introduction** with credentials and avatar
2. **Real-time Chat Interface** with typing indicators
3. **Quick Action Buttons** (Premium calc, tax benefits, schedule call)
4. **Objection Handling** with intelligent responses
5. **Session Analytics** in sidebar

### **Page 4: Analytics** 📊
1. **Recommendation Metrics** (scores, premiums, confidence)
2. **Profile Insights** (risk-return analysis, goal alignment)
3. **Session Analytics** (duration, engagement, lead score)
4. **Performance Charts** (interactive Plotly dashboards)

---

## 🎨 **UI/UX Features**

### **Premium Design Elements**
- **Custom CSS styling** with LIC brand colors (#FF6B35, #004E89)
- **Responsive design** optimized for mobile and desktop
- **Smooth animations** with fade-in effects and loading states
- **Interactive charts** using Plotly for data visualization
- **Professional typography** with consistent spacing and hierarchy

### **Psychological Optimization**
- **Progress indicators** to encourage completion
- **Dynamic messaging** based on user psychology
- **Social proof elements** with success stories and testimonials
- **Urgency creation** through timeline-based incentives
- **Trust building** with agent credentials and experience

### **Accessibility Features**
- **Clear navigation** with sidebar menu and progress tracking
- **Intuitive form design** with helpful tooltips and validation
- **Visual feedback** for user actions and system responses
- **Error handling** with graceful fallbacks and user guidance

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional (for enhanced features)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
```

### **MongoDB Configuration**
- **URI**: `mongodb+srv://madhurambohrawork:tlElRkOBztk1bCJZ@elite-lic-cluster.be1u9gj.mongodb.net/`
- **Database**: `lic_knowledge_base`
- **Collections**: `policy_vectors`, `chat_sessions`

### **Groq LLM Configuration**
- **Model**: `mixtral-8x7b-32768` (High-performance for sales agent)
- **Temperature**: 0.7 (Balanced creativity and consistency)
- **Max Tokens**: 2000 (Comprehensive responses)

---

## 📊 **Success Metrics**

### **Target KPIs**
- **Profile Completion Rate**: >85%
- **Recommendation Engagement**: >70%
- **Chat Session Initiation**: >60%
- **Average Conversation Length**: >5 messages
- **Lead Conversion Rate**: >25%
- **User Satisfaction**: >4.5/5

### **Analytics Tracking**
- **User journey mapping** through profile to chat completion
- **Engagement scoring** based on interaction quality and duration
- **Objection analysis** with resolution tracking
- **Conversion funnel optimization** with A/B testing capabilities

---

## 🛡️ **Security & Performance**

### **Security Features**
- **Environment variable management** for API keys
- **Session state security** with proper data handling
- **Input validation** and sanitization
- **Error handling** with graceful degradation

### **Performance Optimization**
- **Caching strategies** for policy data and recommendations
- **Async processing** for LLM responses
- **Progressive loading** for better user experience
- **Database connection pooling** for optimal performance

---

## 🚀 **Deployment Options**

### **Streamlit Cloud**
```bash
# Deploy to Streamlit Cloud
# 1. Push code to GitHub
# 2. Connect Streamlit Cloud to repository
# 3. Set environment variables in Streamlit Cloud
# 4. Deploy with automatic SSL and scaling
```

### **Custom Server**
```bash
# Deploy on custom server
streamlit run streamlit_dashboard.py --server.port 8501 --server.address 0.0.0.0
```

### **Docker Deployment**
```dockerfile
# Dockerfile included for containerized deployment
# Supports scaling and load balancing
```

---

## 📞 **Support & Maintenance**

### **Monitoring**
- **Application health checks** with system status indicators
- **Performance monitoring** with response time tracking
- **Error logging** with detailed debugging information
- **User analytics** with behavior pattern analysis

### **Updates & Maintenance**
- **Automated model retraining** with performance threshold monitoring
- **Policy data synchronization** with daily scraping updates
- **Feature flag management** for A/B testing and rollouts
- **Backup and recovery** procedures for data protection

---

## 🎯 **Next Steps**

1. **Launch Dashboard**: `streamlit run streamlit_dashboard.py`
2. **Test Complete Flow**: Profile → Recommendations → Chat → Analytics
3. **Monitor Performance**: Check success metrics and user engagement
4. **Optimize Conversion**: A/B test different messaging and UI elements
5. **Scale Deployment**: Move to production environment with monitoring

---

**🏆 Result**: A world-class LIC policy recommendation system that combines cutting-edge AI technology with proven sales psychology to deliver exceptional user experience and high conversion rates.
