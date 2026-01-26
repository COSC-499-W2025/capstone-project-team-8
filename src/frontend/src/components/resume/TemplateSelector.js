import styles from './TemplateSelector.module.css';

export default function TemplateSelector({ templates, onSelectTemplate }) {
  if (!templates || templates.length === 0) {
    return (
      <div className={styles.modal}>
        <div className={styles.modalContent}>
          <h1>No Templates Available</h1>
          <p>No resume templates are currently available. Please try again later.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.modal}>
      <div className={styles.modalContent}>
        <h1>Choose a Resume Template</h1>
        <p className={styles.subtitle}>Select a template to get started with your resume</p>
        
        <div className={styles.templatesGrid}>
          {templates.map((template) => (
            <div 
              key={template.id} 
              className={styles.templateCard}
              onClick={() => onSelectTemplate(template)}
            >
              <div className={styles.templatePreview}>
                {template.preview_image && (
                  <img src={template.preview_image} alt={template.name} />
                )}
                {!template.preview_image && (
                  <div className={styles.placeholderPreview}>
                    <span>📄</span>
                  </div>
                )}
              </div>
              <div className={styles.templateInfo}>
                <h3>{template.name}</h3>
                {template.description && (
                  <p>{template.description}</p>
                )}
              </div>
              <button className={styles.selectBtn}>
                Select Template
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
