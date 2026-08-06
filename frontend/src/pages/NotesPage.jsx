import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { getNotes, saveNote, deleteNote } from '@/services/noteService';

const NotesPage = () => {
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState({ title: '', content: '' });

  useEffect(() => {
    getNotes().then(setNotes);
  }, []);

  const handleSave = async () => {
    if (!newNote.title.trim() || !newNote.content.trim()) return;
    const saved = await saveNote(newNote);
    setNotes([...notes, saved]);
    setNewNote({ title: '', content: '' });
  };

  const handleDelete = async (id) => {
    await deleteNote(id);
    setNotes(notes.filter(n => n.id !== id));
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Notes</h1>
      <Card className="p-4 mb-4">
        <div className="space-y-2">
          <Input
            placeholder="Title"
            value={newNote.title}
            onChange={(e) => setNewNote({ ...newNote, title: e.target.value })}
          />
          <Textarea
            placeholder="Content"
            value={newNote.content}
            onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
            rows={4}
          />
          <Button onClick={handleSave}>Save Note</Button>
        </div>
      </Card>
      <div className="space-y-3">
        {notes.map(note => (
          <Card key={note.id} className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-bold">{note.title}</h3>
                <p className="text-sm text-muted-foreground">{note.content}</p>
              </div>
              <Button variant="destructive" size="sm" onClick={() => handleDelete(note.id)}>Delete</Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default NotesPage;
