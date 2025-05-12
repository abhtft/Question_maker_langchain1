import gc
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024  # Convert to MB

def cleanup_memory():
    gc.collect()

class CreatePDF:
    @staticmethod
    def generate(questions, filename, class_grade='', subject_name='', include_answers=False):
        try:
            # Monitor initial memory
            initial_memory = monitor_memory()
            logging.info(f"PDF Generation - Initial memory: {initial_memory:.2f} MB")

            # Create buffer
            buffer = BytesIO()
            
            # Create PDF with optimized settings
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )

            # Build content in chunks
            elements = []
            
            # Add header
            elements.extend([
                Paragraph(f"Class: {class_grade}", styles['Heading1']),
                Paragraph(f"Subject: {subject_name}", styles['Heading1']),
                Spacer(1, 20)
            ])

            # Process questions in smaller chunks
            chunk_size = 5
            for i in range(0, len(questions), chunk_size):
                chunk = questions[i:i + chunk_size]
                
                for q in chunk:
                    # Add question
                    elements.append(Paragraph(f"Q{i+1}. {q['question']}", styles['Normal']))
                    elements.append(Spacer(1, 10))
                    
                    # Add options
                    for opt in q['options']:
                        elements.append(Paragraph(f"{opt}", styles['Normal']))
                    
                    elements.append(Spacer(1, 10))
                    
                    # Add answer if requested
                    if include_answers:
                        elements.append(Paragraph(f"Answer: {q['answer']}", styles['Normal']))
                        elements.append(Spacer(1, 10))
                    
                    # Cleanup after each question
                    if i % 10 == 0:
                        cleanup_memory()
                
                # Log memory usage
                current_memory = monitor_memory()
                logging.info(f"PDF Generation - Memory after chunk {i//chunk_size + 1}: {current_memory:.2f} MB")

            # Build PDF
            doc.build(elements)
            
            # Get the value of the BytesIO buffer
            pdf = buffer.getvalue()
            buffer.close()
            
            # Final cleanup
            cleanup_memory()
            final_memory = monitor_memory()
            logging.info(f"PDF Generation - Final memory: {final_memory:.2f} MB")
            
            return BytesIO(pdf)

        except Exception as e:
            logging.error(f"Error in PDF generation: {e}")
            raise
        finally:
            # Ensure cleanup happens
            cleanup_memory() 