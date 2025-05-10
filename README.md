Absolutely! Here’s a comprehensive documentation for your current project, covering deployment, usage, architecture, and future plans. You can use this as your README.md or internal documentation.
Prashnotri – AI Question Paper Generator
Overview
Prashnotri is an AI-powered platform for generating high-quality, customized question papers. It leverages OpenAI for question generation, supports feedback-driven improvement, and stores generated papers and user uploads securely on AWS S3. The app is built with a Python Flask backend, React frontend, and MongoDB for data storage.
Features
Generate question papers based on subject, class, topic, difficulty, Bloom’s level, and intelligence type/subtype.
Store and serve generated PDFs from AWS S3.
User feedback system for continuous improvement.
Secure, scalable deployment on AWS EC2 with Nginx and HTTPS.
(Planned) Upload notes as PDF/images for context-aware question generation.
Tech Stack
Backend: Python (Flask), OpenAI API, MongoDB, AWS S3, Boto3
Frontend: React (TypeScript)
Deployment: Ubuntu EC2, Nginx, PM2 (or systemd), Certbot (Let’s Encrypt SSL)
Other: Python virtualenv, dotenv for secrets
Directory Structure
Apply to README.md
Environment Variables (.env)
Apply to README.md
Deployment Steps
1. Server Setup
Launch Ubuntu EC2 instance.
Open ports 22 (SSH), 80 (HTTP), 443 (HTTPS) in security group.
2. Install Dependencies
Apply to README.md
Run
3. Clone and Set Up Project
Apply to README.md
Run
4. Configure Environment
Create .env file with your secrets.
5. Frontend Build
Build your React frontend locally:
Apply to README.md
Run
Copy the build output to the dist/ folder on your server.
6. Nginx Setup
Create /etc/nginx/sites-available/prashnotri.com:
Apply to README.md
Enable site and restart Nginx:
Apply to README.md
Run
7. SSL with Certbot
Apply to README.md
Run
8. Run Flask App with PM2
Apply to README.md
Run
Usage
Access the app:
Go to https://prashnotri.com in your browser.
Fill in the form:
Subject, class, language, topics, question type, difficulty, Bloom’s level, intelligence type, and subtype.
Add additional instructions if needed.
Submit:
The app generates a question paper and provides a PDF download link.
Feedback:
Users can submit feedback on generated papers for future improvement.
Intelligence Types & Subtypes
| Intelligence | Refined SubTypes (Examples) |
| -------------- | --------------------------------------------------------------- |
| Logical | Pattern solving, Deductive reasoning, Coding logic, Data interpretation |
| Linguistic | Storytelling, Persuasive argument, Vocabulary building, Creative writing |
| Kinesthetic | Gross motor (e.g., sports), Fine motor (e.g., drawing), Simulations |
| Spatial | 3D visualization, Map reading, Mental rotation, Blueprint understanding |
| Musical | Rhythm patterns, Composition, Tone recognition |
| Interpersonal | Negotiation skills, Group collaboration, Empathy exercises |
| Intrapersonal | Self-assessment, Reflective writing, Goal setting |
| Naturalistic | Classification tasks, Field observations, Environmental problem-solving |
Prompt Engineering
Prompts are detailed, with strict requirements for question quality, format, and explanation.
Example and “Do Not” sections are included for clarity.
Feedback from users is incorporated into future prompt generations.
Feedback & Improvement Plan
Collect user feedback on question quality.
Iteratively refine prompts and add features (PDF upload, analytics, etc.).
Monitor logs and performance for stability.
Prepare for public launch after 1–2 months of testing and improvement.
Future Features
PDF/image upload for context-aware question generation.
Analytics dashboard for usage and feedback.
Enhanced user management and authentication.
More advanced feedback integration and prompt tuning.
Troubleshooting
502 Bad Gateway: Ensure Flask app is running and PM2 is managing it.
SSL Issues: Check Certbot and Nginx config.
App not running after reboot: Make sure pm2 save and pm2 startup were run.
Logs:
Flask: pm2 logs prashnotri
Nginx: sudo tail -n 50 /var/log/nginx/error.log
Contact & Support
For issues, open a GitHub issue or contact the maintainer.
For deployment or feature requests, reach out via email or the project’s contact form.
Congratulations on your deployment!
You are set up for iterative improvement and a successful public launch.
Let me know if you want this as a markdown file, or if you want to add/change any section!


cd C:\Users\Abhishek\Desktop\pem_work
ssh -i abhi.pem ubuntu@ec2-43-204-212-194.ap-south-1.compute.amazonaws.com

 #feedback system in frontend
 #note taking feature are important
 #issue with the falsk async options
 

