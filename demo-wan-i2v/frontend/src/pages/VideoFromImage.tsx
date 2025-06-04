// frontend/src/pages/VideoFromImage.tsx
import React, { useState, ChangeEvent } from "react";
import axios from "axios";

const VideoFromImage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [prompt, setPrompt] = useState<string>("");         // например, текстовый prompt
  const [negPrompt, setNegPrompt] = useState<string>("");   // negative prompt
  const [jobId, setJobId] = useState<string>("");
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [status, setStatus] = useState<"idle" | "submitted" | "running" | "completed" | "failed">("idle");

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const onPromptChange = (e: ChangeEvent<HTMLInputElement>) => {
    setPrompt(e.target.value);
  };
  const onNegPromptChange = (e: ChangeEvent<HTMLInputElement>) => {
    setNegPrompt(e.target.value);
  };

  const submitImage = async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("prompt", prompt);
    formData.append("neg_prompt", negPrompt);
    formData.append("duration_sec", "5");      // всегда 5 сек
    formData.append("fps", "16");              // всегда 16 fps
    formData.append("num_inference_steps", "25"); // по умолчанию 25, можно сделать input

    setStatus("submitted");
    try {
      const resp = await axios.post("/api/i2v/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const newJobId = resp.data.job_id;
      setJobId(newJobId);
      setStatus("running");
      pollStatus(newJobId);
    } catch (err) {
      console.error(err);
      setStatus("failed");
    }
  };

  const pollStatus = (id: string) => {
    const interval = setInterval(async () => {
      try {
        const resp = await axios.get(`/api/i2v/${id}`);
        const data = resp.data;
        if (data.status === "running") {
          setStatus("running");
        } else if (data.status === "completed") {
          // data.video_url = "/videos/<jobId>.mp4"
          setVideoUrl(data.video_url);
          setStatus("completed");
          clearInterval(interval);
        } else if (data.status === "failed") {
          setStatus("failed");
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
        setStatus("failed");
        clearInterval(interval);
      }
    }, 3000);
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl mb-4">Генерация видео (5 сек, 1280×720, 16 fps)</h1>

      <div className="mb-2">
        <label className="block mb-1">Prompt:</label>
        <input
          type="text"
          value={prompt}
          onChange={onPromptChange}
          className="w-full p-2 border rounded"
          placeholder="Опишите желаемое содержание"
        />
      </div>
      <div className="mb-2">
        <label className="block mb-1">Negative Prompt:</label>
        <input
          type="text"
          value={negPrompt}
          onChange={onNegPromptChange}
          className="w-full p-2 border rounded"
          placeholder="Что не должно быть на видео"
        />
      </div>

      <input type="file" accept="image/*" onChange={onFileChange} />
      <button
        onClick={submitImage}
        disabled={!selectedFile || status === "running"}
        className="mt-3 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {status === "running" ? "Генерация..." : "Сгенерировать"}
      </button>

      {status === "running" && <p className="mt-2 text-blue-500">Идёт генерация...</p>}
      {status === "failed" && <p className="mt-2 text-red-500">Ошибка при генерации.</p>}

      {status === "completed" && videoUrl && (
        <div className="mt-4">
          <h2 className="text-xl mb-2">Ваше видео:</h2>
          <video src={videoUrl} controls width="640" height="360" />
        </div>
      )}
    </div>
  );
};

export default VideoFromImage;
