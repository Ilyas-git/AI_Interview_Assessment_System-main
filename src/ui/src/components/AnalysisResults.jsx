import React from 'react';
import { 
  CheckCircle, AlertCircle, TrendingUp, MessageSquare, 
  Brain, Mic, Target, RotateCcw 
} from 'lucide-react';

const ScoreCard = ({ title, score, icon: Icon, color }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getProgressColor = (score) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div className="glass-panel p-4 flex flex-col">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-5 h-5 ${color}`} />
        <span className="text-sm text-gray-400">{title}</span>
      </div>
      <div className={`text-3xl font-bold ${getScoreColor(score)}`}>
        {score}%
      </div>
      <div className="mt-2 h-2 bg-white/10 rounded-full overflow-hidden">
        <div 
          className={`h-full ${getProgressColor(score)} transition-all duration-500`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
};

const FeedbackSection = ({ title, items, icon: Icon }) => (
  <div className="glass-panel p-4">
    <div className="flex items-center gap-2 mb-3">
      <Icon className="w-5 h-5 text-primary-color" />
      <h4 className="font-semibold">{title}</h4>
    </div>
    <ul className="space-y-2">
      {items.map((item, index) => (
        <li key={index} className="flex items-start gap-2 text-sm text-gray-300">
          <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  </div>
);

const AnalysisResults = ({ results, transcription, onReset }) => {
  if (!results || !transcription) {
    return null;
  }

  const { scores, feedback, details } = results;

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 animate-fade-in-up">
      {/* Header */}
      <div className="glass-panel p-6 text-center">
        <div className="flex items-center justify-center gap-3 mb-2">
          <Brain className="w-8 h-8 text-primary-color" />
          <h2 className="text-2xl font-bold">Analysis Complete</h2>
        </div>
        <p className="text-gray-400">Here's how you performed in this interview response</p>
      </div>

      {/* Overall Score */}
      <div className="glass-panel p-6 text-center">
        <h3 className="text-lg text-gray-400 mb-2">Overall Score</h3>
        <div className={`text-6xl font-bold ${
          scores.overall >= 80 ? 'text-green-400' :
          scores.overall >= 60 ? 'text-yellow-400' :
          scores.overall >= 40 ? 'text-orange-400' : 'text-red-400'
        }`}>
          {scores.overall}%
        </div>
        <p className="mt-3 text-gray-300">{feedback.overall[0]}</p>
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ScoreCard 
          title="Clarity" 
          score={scores.clarity} 
          icon={MessageSquare}
          color="text-blue-400"
        />
        <ScoreCard 
          title="Confidence" 
          score={scores.confidence} 
          icon={Mic}
          color="text-purple-400"
        />
        <ScoreCard 
          title="Relevance" 
          score={scores.relevance} 
          icon={Target}
          color="text-cyan-400"
        />
      </div>

      {/* Transcription */}
      <div className="glass-panel p-6">
        <div className="flex items-center gap-2 mb-4">
          <MessageSquare className="w-5 h-5 text-primary-color" />
          <h3 className="text-lg font-semibold">Your Response (Transcription)</h3>
        </div>
        <p className="text-gray-300 leading-relaxed bg-black/20 p-4 rounded-lg">
          {transcription.text}
        </p>
        {details.clarity && (
          <div className="mt-3 flex gap-4 text-sm text-gray-400">
            <span>Words: {details.clarity.word_count}</span>
            <span>Sentences: {details.clarity.sentence_count}</span>
            <span>Vocabulary Variety: {details.clarity.vocabulary_variety}%</span>
          </div>
        )}
      </div>

      {/* Detailed Feedback */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FeedbackSection 
          title="Clarity Feedback" 
          items={feedback.clarity} 
          icon={MessageSquare}
        />
        <FeedbackSection 
          title="Confidence Feedback" 
          items={feedback.confidence} 
          icon={Mic}
        />
      </div>
      
      <FeedbackSection 
        title="Relevance & Technical Content" 
        items={feedback.relevance} 
        icon={Target}
      />

      {/* Technical Terms Used */}
      {details.relevance?.technical_terms?.counts && 
       Object.keys(details.relevance.technical_terms.counts).length > 0 && (
        <div className="glass-panel p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <h3 className="text-lg font-semibold">Technical Terms Detected</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(details.relevance.technical_terms.counts).map(([term, count]) => (
              <span 
                key={term}
                className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm"
              >
                {term} ({count})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Filler Words Warning */}
      {details.confidence?.filler_words?.total > 0 && (
        <div className="glass-panel p-6 border-orange-500/30">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-orange-400" />
            <h3 className="text-lg font-semibold">Filler Words Detected</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(details.confidence.filler_words.counts).map(([word, count]) => (
              <span 
                key={word}
                className="px-3 py-1 bg-orange-500/20 text-orange-400 rounded-full text-sm"
              >
                "{word}" ({count}x)
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Reset Button */}
      <div className="flex justify-center pt-4">
        <button 
          onClick={onReset}
          className="btn-secondary flex items-center gap-2 px-8"
        >
          <RotateCcw className="w-4 h-4" />
          Try Another Response
        </button>
      </div>
    </div>
  );
};

export default AnalysisResults;
