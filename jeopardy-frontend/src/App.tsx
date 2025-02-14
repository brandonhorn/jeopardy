// src/App.tsx
import React, { useEffect, useState } from 'react';
import JeopardyQuestion from './JeopardyQuestion';
import { JeopardyData } from './models';
import { getJeopardyQuestion } from './api';

const App = () => {
  const [data, setData] = useState<JeopardyData>();
  const [currentIndex, setCurrentIndex] = useState(0);

  const getClue = async () => {
    const response = await getJeopardyQuestion();
    setData(response);
  };

  useEffect(() => {
    getClue();
  }, []);

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <JeopardyQuestion
        key={data.Id}
        data={data}
        onSubmit={() => getClue()}
      />
      <button
        onClick={() => getClue()}
      >
        Next Question
      </button>
    </div>
  );
};

export default App;