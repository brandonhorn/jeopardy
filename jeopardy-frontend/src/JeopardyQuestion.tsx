// src/JeopardyQuestion.tsx
import React, { useState } from 'react';
import { submitJeopardyQuestion} from './api';
import { JeopardyData } from './models';
import styles from "./JeopardyQuestion.module.css";

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

  const submitState = (save: boolean) => {
    if (save) {
      submitJeopardyQuestion(clue.Id, clue.Value, ringIn ? (isCorrect ? 1 : -1) : 0);
    }
    onSubmit();
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>{clue.Category} - ${clue.Value}</h2>
      <p className={styles.question}>{clue.Question}</p>
      <div className={styles.actions}>
        <button className={styles.buzz} onClick={() => setRingIn(!ringIn)}>{ringIn ? "Buzz" : "un-Buzz"}</button>
        <button onClick={handleSubmit}>Reveal</button>
      </div>
      
      {!!ringIn && <input
        type="text"
        value={userResponse}
        onChange={(e) => setUserResponse(e.target.value)}
      />}
      
      {isCorrect !== null && (
        <div className={styles.answerReveal}>
          <p>{isCorrect ? 'Correct!' : 'Incorrect!'}</p>
          <p>The answer was: {clue.Answer}</p>
          <button disabled={isCorrect} onClick={() => setIsCorrect(true)}>Mark as Correct</button>
          <button disabled={!isCorrect} onClick={() => setIsCorrect(false)}>Mark as Incorrect</button>
        </div>
      )}
       <div className={styles.actions}>
            <button onClick={() => submitState(true)}>Save and Continue </button>
            <button onClick={() => submitState(false)}>Continue without Saving</button> 
       </div>
    </div>
  );
};

export default JeopardyQuestion;