import styles from './ResumePreview.module.css';

export default function ResumePreview({ content, template }) {
  return (
    <div id="resume-preview" className={styles.preview}>
      <div className={styles.header}>
        <h1 className={styles.title}>Resume Preview</h1>
        {template && (
          <p className={styles.templateName}>
            Template: <strong>{template.name}</strong>
          </p>
        )}
      </div>

      {/* Projects Section */}
      {content.sections.projects && content.sections.projects.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Project Experience</h2>
          <ul className={styles.list}>
            {content.sections.projects.map(bullet => (
              <li key={bullet.id} className={styles.listItem}>
                {bullet.text}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Experience Section */}
      {content.sections.experience && content.sections.experience.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Experience</h2>
          {content.sections.experience.map(item => (
            <div key={item.id} className={styles.item}>
              <div className={styles.itemHeader}>
                <h3 className={styles.itemTitle}>{item.title || 'Job Title'}</h3>
                <p className={styles.itemCompany}>{item.company || 'Company'}</p>
              </div>
              {item.content && (
                <p className={styles.itemContent}>{item.content}</p>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Education Section */}
      {content.sections.education && content.sections.education.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Education</h2>
          {content.sections.education.map(item => (
            <div key={item.id} className={styles.item}>
              <div className={styles.itemHeader}>
                <h3 className={styles.itemTitle}>
                  {item.degree} {item.field && `in ${item.field}`}
                </h3>
                <p className={styles.itemCompany}>{item.school}</p>
              </div>
            </div>
          ))}
        </section>
      )}

      {/* Skills Section */}
      {content.sections.skills && content.sections.skills.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Skills</h2>
          {content.sections.skills.map(item => (
            <div key={item.id} className={styles.skillsItem}>
              {item.category && (
                <h3 className={styles.skillsCategory}>{item.category}</h3>
              )}
              {item.content && (
                <p className={styles.skillsList}>{item.content}</p>
              )}
            </div>
          ))}
        </section>
      )}

      {!content.sections.projects?.length &&
        !content.sections.experience?.length &&
        !content.sections.education?.length &&
        !content.sections.skills?.length && (
          <div className={styles.emptyPreview}>
            <p>No content yet. Add bullet points and sections to see the preview.</p>
          </div>
        )}
    </div>
  );
}
