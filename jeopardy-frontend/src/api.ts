// write api client to call into python backend

import { JeopardyData } from "./models";

const BACKEND_URI = "http://127.0.0.1:5000";

export async function getJeopardyQuestion(): Promise<JeopardyData> {
    const response = await fetch(`${BACKEND_URI}/api/question`, {
        method: "GET"
    });

    return (await response.json()) as JeopardyData;
}

export async function submitJeopardyQuestion(clue_id: number, value: number, isCorrect: number): Promise<void> {
    await fetch(`${BACKEND_URI}/api/player/${0}/clue`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
            clue_id,
            value,
            'correct': isCorrect })
    });
}