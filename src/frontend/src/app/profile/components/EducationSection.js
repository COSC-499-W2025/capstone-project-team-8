import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { addEducation, updateEducation, deleteEducation } from '@/utils/api';
import config from '@/config';

export default function EducationSection() {
  const { token } = useAuth();
  const [educations, setEducations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  
  // To handle the edit state, track which item is being edited. New items have id 'new'.
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState(null);

  const fetchEducation = async () => {
    try {
      const response = await fetch(`${config.API_URL}/api/education/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch education');
      const data = await response.json();
      setEducations(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchEducation();
    }
  }, [token]);

  const handleEdit = (edu) => {
    setEditingId(edu.id);
    setEditForm({ ...edu });
  };

  const handleAddNew = () => {
    setEditingId('new');
    setEditForm({
      institution: '',
      major: '',
      degree: '',
      location: '',
      start_date: '',
      end_date: '',
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditForm(null);
  };

  const saveEdit = async () => {
    setSaving(true);
    setError('');
    try {
        const payload = {
            institution: editForm.institution || 'University',
            major: editForm.major || '',
            degree: editForm.degree || '',
            location: editForm.location || '',
            start_date: editForm.start_date || null,
            end_date: editForm.end_date || null,
        };
      if (editingId === 'new') {
        await addEducation(payload, token);
      } else {
        await updateEducation(editingId, payload, token);
      }
      await fetchEducation();
      setEditingId(null);
      setEditForm(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this education entry?')) return;
    try {
      await deleteEducation(id, token);
      await fetchEducation();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="text-white/60 mb-6">Loading education history...</div>;

  return (
    <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-white">Education History</h2>
        {!editingId && (
          <button 
            type="button"
            onClick={handleAddNew}
            className="text-sm px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded transition"
          >
            + Add Education
          </button>
        )}
      </div>

      {error && <div className="mb-4 text-red-400 text-sm">{error}</div>}

      <div className="space-y-4">
        {educations.length === 0 && !editingId && (
          <p className="text-white/60 text-sm italic">No education history added yet.</p>
        )}

        {educations.map(edu => (
          <div key={edu.id} className="border border-white/10 p-4 rounded-lg bg-white/5 flex flex-col md:flex-row justify-between items-start md:items-center transition-all">
            {editingId === edu.id ? (
               <EditForm 
                 form={editForm} 
                 setForm={setEditForm} 
                 onSave={saveEdit} 
                 onCancel={cancelEdit} 
                 saving={saving} 
               />
            ) : (
              <>
                <div className="mb-4 md:mb-0">
                  <h3 className="text-white font-medium text-lg leading-tight">{edu.institution}</h3>
                  <p className="text-white/80 text-sm mt-1">{edu.degree ? `${edu.degree} in ` : ''}{edu.major}</p>
                  <p className="text-white/50 text-xs mt-1">
                    {edu.location} {edu.location && (edu.start_date || edu.end_date) ? ' | ' : ''} 
                    {edu.start_date ? edu.start_date.substring(0,4) + ' - ' : ''}
                    {edu.end_date ? edu.end_date.substring(0,4) : (edu.currently_studying ? 'Present' : '')}
                  </p>
                </div>
                <div className="flex space-x-3 shrink-0">
                  <button onClick={() => handleEdit(edu)} className="text-sm px-2 py-1 text-blue-400 hover:text-blue-300 hover:bg-blue-400/10 rounded transition">Edit</button>
                  <button onClick={() => handleDelete(edu.id)} className="text-sm px-2 py-1 text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded transition">Delete</button>
                </div>
              </>
            )}
          </div>
        ))}

        {editingId === 'new' && (
          <div className="border border-white/10 p-5 rounded-lg bg-white/10 relative shadow-lg">
            <h3 className="text-white font-medium mb-4">Add New Education</h3>
            <EditForm 
              form={editForm} 
              setForm={setEditForm} 
              onSave={saveEdit} 
              onCancel={cancelEdit} 
              saving={saving} 
            />
          </div>
        )}
      </div>
    </div>
  );
}

function EditForm({ form, setForm, onSave, onCancel, saving }) {
  const handleChange = (e) => setForm({...form, [e.target.name]: e.target.value});
  
  return (
    <div className="w-full space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <label className="block text-white/80 text-xs font-medium mb-1">Institution / School <span className="text-red-400">*</span></label>
          <input name="institution" value={form.institution} onChange={handleChange} className="w-full px-3 py-2 rounded-md bg-black/40 border border-white/20 text-sm text-white focus:outline-none focus:border-white/50 transition" placeholder="University Name" />
        </div>
        <div>
          <label className="block text-white/80 text-xs font-medium mb-1">Major / Program</label>
          <input name="major" value={form.major} onChange={handleChange} className="w-full px-3 py-2 rounded-md bg-black/40 border border-white/20 text-sm text-white focus:outline-none focus:border-white/50 transition" placeholder="Computer Science" />
        </div>
        <div>
          <label className="block text-white/80 text-xs font-medium mb-1">Degree Type</label>
          <input name="degree" value={form.degree} onChange={handleChange} className="w-full px-3 py-2 rounded-md bg-black/40 border border-white/20 text-sm text-white focus:outline-none focus:border-white/50 transition" placeholder="BSc" />
        </div>
        <div className="md:col-span-2">
          <label className="block text-white/80 text-xs font-medium mb-1">Location</label>
          <input name="location" value={form.location} onChange={handleChange} className="w-full px-3 py-2 rounded-md bg-black/40 border border-white/20 text-sm text-white focus:outline-none focus:border-white/50 transition" placeholder="City, State" />
        </div>
        <div>
          <label className="block text-white/80 text-xs font-medium mb-1">Start Date</label>
          <input type="date" name="start_date" value={form.start_date || ''} onChange={handleChange} className={`w-full px-3 py-2 rounded-md bg-black/40 border border-white/20 text-sm transition focus:outline-none focus:border-white/50 ${form.start_date ? 'text-white' : 'text-white/40'}`} />
        </div>
        <div>
          <label className="block text-white/80 text-xs font-medium mb-1">End / Expected Graduation Date</label>
          <input type="date" name="end_date" value={form.end_date || ''} onChange={handleChange} className={`w-full px-3 py-2 rounded-md bg-black/40 border border-white/20 text-sm transition focus:outline-none focus:border-white/50 ${form.end_date ? 'text-white' : 'text-white/40'}`} />
        </div>
      </div>
      <div className="flex justify-end space-x-3 pt-4 mt-2 border-t border-white/10">
        <button type="button" onClick={onCancel} disabled={saving} className="px-4 py-1.5 rounded text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 transition disabled:opacity-50">Cancel</button>
        <button type="button" onClick={onSave} disabled={saving} className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm rounded transition shadow-lg shadow-blue-900/40 disabled:opacity-50">{saving ? 'Saving...' : 'Save Entry'}</button>
      </div>
    </div>
  );
}
