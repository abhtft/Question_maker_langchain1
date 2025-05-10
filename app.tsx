import React, { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';

// Comment out intelligence level and number of questions for now
// const intelligenceLevel = formData.intelligenceLevel;
// const numQuestions = formData.numQuestions; 

interface FormData {
  subjectName: string;
  classGrade: string;
  language: string;
  numTopics: number;
  topics: Array<{
    sectionName: string;
    numQuestions: number;
    questionType: string;
    difficulty: string;
    bloomLevel: string;
    intelligenceType: string;
    additionalInstructions?: string;
  }>;
}

const QuestionPaperGenerator = () => {
  const { register, handleSubmit, control } = useForm();
  const { fields, append, remove } = useFieldArray({
    control,
    name: "topics"
  });
  const [uploadingFile, setUploadingFile] = useState(false);
  const [uploadedFileId, setUploadedFileId] = useState<string | null>(null);

  const handleFileUpload = async (file: File) => {
    try {
      setUploadingFile(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:5000/api/upload-note', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        setUploadedFileId(data.note_id);
        alert('File uploaded successfully!');
      } else {
        alert(data.error || 'Failed to upload file');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload file');
    } finally {
      setUploadingFile(false);
    }
  };

  const onSubmit = async (data: any) => {
    try {
      // Add the uploaded file ID to the form data if it exists
      if (uploadedFileId) {
        data.topics = data.topics.map((topic: any) => ({
          ...topic,
          noteId: uploadedFileId
        }));
      }

      const response = await fetch('http://localhost:5000/api/generate-questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      if (result.success) {
        alert('Questions generated successfully!');
        // Handle success (e.g., show questions, download PDF)
      } else {
        alert(result.error || 'Failed to generate questions');
      }
    } catch (error) {
      console.error('Error generating questions:', error);
      alert('Failed to generate questions');
    }
  };

  return (
    <div className="container">
      <h1>Question Paper Generator</h1>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="form-group">
          <label>Subject Name *</label>
          <input {...register("subjectName", { required: true })} />
        </div>

        <div className="form-group">
          <label>Class/Grade *</label>
          <input {...register("classGrade", { required: true })} />
        </div>

        <div className="form-group">
          <label>Language *</label>
          <select {...register("language", { required: true })}>
            <option value="">Select Language</option>
            <option value="English">English</option>
            <option value="Hindi">Hindi</option>
          </select>
        </div>

        <div className="form-group">
          <label>Upload Notes (PDF)</label>
          <div className="file-upload-container">
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  handleFileUpload(file);
                }
              }}
              disabled={uploadingFile}
              style={{ display: 'none' }}
              id="file-upload"
            />
            <label htmlFor="file-upload" className="file-upload-button">
              {uploadingFile ? 'Uploading...' : 'Choose File'}
            </label>
            {uploadedFileId && (
              <span className="file-upload-success">✓ File uploaded successfully</span>
            )}
          </div>
        </div>

        <div className="form-group">
          <label>Number of Topics *</label>
          <input
            type="number"
            min="1"
            max="10"
            {...register("numTopics", { required: true, min: 1, max: 10 })}
          />
        </div>

        {fields.map((field, index) => (
          <div key={field.id} className="topic-section">
            <h3>Topic {index + 1}</h3>
            <div className="form-group">
              <label>Section Name *</label>
              <input
                {...register(`topics.${index}.sectionName`, { required: true })}
              />
            </div>
            <div className="form-group">
              <label>Number of Questions *</label>
              <input
                type="number"
                min="1"
                max="20"
                {...register(`topics.${index}.numQuestions`, {
                  required: true,
                  min: 1,
                  max: 20,
                })}
              />
            </div>
            <div className="form-group">
              <label>Question Type *</label>
              <select
                {...register(`topics.${index}.questionType`, { required: true })}
              >
                <option value="">Select Type</option>
                <option value="MCQ">MCQ</option>
                <option value="Short Answer">Short Answer</option>
                <option value="Long Answer">Long Answer</option>
              </select>
            </div>
            <div className="form-group">
              <label>Difficulty Level *</label>
              <select
                {...register(`topics.${index}.difficulty`, { required: true })}
              >
                <option value="">Select Difficulty</option>
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
            <div className="form-group">
              <label>Bloom's Taxonomy Level *</label>
              <select
                {...register(`topics.${index}.bloomLevel`, { required: true })}
              >
                <option value="">Select Level</option>
                <option value="Remember">Remember</option>
                <option value="Understand">Understand</option>
                <option value="Apply">Apply</option>
                <option value="Analyze">Analyze</option>
                <option value="Evaluate">Evaluate</option>
                <option value="Create">Create</option>
              </select>
            </div>
            <div className="form-group">
              <label>Intelligence Type *</label>
              <select
                {...register(`topics.${index}.intelligenceType`, {
                  required: true,
                })}
              >
                <option value="">Select Type</option>
                <option value="Logical">Logical</option>
                <option value="Verbal">Verbal</option>
                <option value="Visual">Visual</option>
                <option value="Musical">Musical</option>
                <option value="Bodily">Bodily</option>
                <option value="Interpersonal">Interpersonal</option>
                <option value="Intrapersonal">Intrapersonal</option>
                <option value="Naturalistic">Naturalistic</option>
              </select>
            </div>
            <div className="form-group">
              <label>Additional Instructions</label>
              <textarea
                {...register(`topics.${index}.additionalInstructions`)}
                placeholder="Any specific instructions for this topic..."
              />
            </div>
            <button
              type="button"
              onClick={() => remove(index)}
              className="remove-topic"
            >
              Remove Topic
            </button>
          </div>
        ))}

        <button type="submit" className="submit-button">
          Generate Questions
        </button>
      </form>
    </div>
  );
};

export default QuestionPaperGenerator; 