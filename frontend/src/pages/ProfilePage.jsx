import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { getProfile, updateProfile } from '@/services/userService';

const ProfilePage = () => {
  const [profile, setProfile] = useState({});
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    getProfile().then(setProfile);
  }, []);

  const handleSave = async () => {
    await updateProfile(profile);
    setEditing(false);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Profile</h1>
      <Card className="p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-bold mb-1">Name</label>
            <Input
              value={profile.name || ''}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
              disabled={!editing}
            />
          </div>
          <div>
            <label className="block text-sm font-bold mb-1">Email</label>
            <Input
              value={profile.email || ''}
              onChange={(e) => setProfile({ ...profile, email: e.target.value })}
              disabled={!editing}
            />
          </div>
          <div>
            <label className="block text-sm font-bold mb-1">Firm</label>
            <Input
              value={profile.firm || ''}
              onChange={(e) => setProfile({ ...profile, firm: e.target.value })}
              disabled={!editing}
            />
          </div>
          <div>
            <label className="block text-sm font-bold mb-1">Role</label>
            <Input
              value={profile.role || ''}
              onChange={(e) => setProfile({ ...profile, role: e.target.value })}
              disabled={!editing}
            />
          </div>
          {editing ? (
            <Button onClick={handleSave}>Save</Button>
          ) : (
            <Button onClick={() => setEditing(true)}>Edit</Button>
          )}
        </div>
      </Card>
    </div>
  );
};

export default ProfilePage;
