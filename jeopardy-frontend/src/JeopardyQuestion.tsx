// src/JeopardyQuestion.tsx
import React, { useState } from 'react';
import { submitJeopardyQuestion} from './api';
import { JeopardyData } from './models';

export interface IJeopardyQuestionProps {
    data: JeopardyData;
    onSubmit: () => void;
}

const JeopardyQuestion: React.FC<IJeopardyQuestionProps> = ({data: clue, onSubmit}) => {
  const [userResponse, setUserResponse] = useState('');
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [ringIn, setRingIn] = useState(false);

  const handleSubmit = () => {
    setIsCorrect(userResponse.trim().toLowerCase() === clue.Answer.trim().toLowerCase());
  };

  const submitState = () => {
    submitJeopardyQuestion(clue.Id, clue.Value, ringIn ? (isCorrect ? 1 : -1) : 0);
    onSubmit();
  }

  return (
    <div>
      <h2>{clue.Category} - ${clue.Value}</h2>
      <p>{clue.Question}</p>
      <button onClick={() => setRingIn(true)}>Buzz</button>
      {!!ringIn && <input
        type="text"
        value={userResponse}
        onChange={(e) => setUserResponse(e.target.value)}
      />}
      <button onClick={handleSubmit}>Submit</button>
      {isCorrect !== null && (
        <div>
          <p>{isCorrect ? 'Correct!' : 'Incorrect!'}</p>
          <p>The answer was: {clue.Answer}</p>
          <button onClick={() => setIsCorrect(true)}>Mark as Correct</button>
          <button onClick={() => setIsCorrect(false)}>Mark as Incorrect</button>
        </div>
      )}
        <button onClick={submitState}>Submit State </button>
    </div>
  );
};

export default JeopardyQuestion;