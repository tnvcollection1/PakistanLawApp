import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Scale, BookOpen, Search, Shield, ArrowRight, Eye, EyeOff, Loader2, ArrowLeft } from 'lucide-react';
import { authAPI } from '../api/api';
import { Checkbox } from '../components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstName: '', lastName: '', email: '', phone: '',
    username: '', password: '', confirmPassword: '',
    profession: '', city: '', country: 'pakistan', address: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [agreedTerms, setAgreedTerms] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const [stats, setStats] = useState([
    { value: '194,167', label: 'Case Laws' },
    { value: '22,590', label: 'Statutes' },
    { value: '38,079', label: 'Dictionary' },
    { value: '16,161', label: "Black's Law" },
  ]);

  useEffect(() => {
    fetch('/api/stats')
      .then(r => r.json())
      .then(data => {
        if (data?.homepage) {
          setStats([
            { value: data.homepage.case_laws.toLocaleString(), label: 'Case Laws' },
            { value: data.homepage.statutes.toLocaleString(), label: 'Statutes' },
            { value: data.homepage.dictionary.toLocaleString(), label: 'Dictionary' },
            { value: data.homepage.blacks_law.toLocaleString(), label: "Black's Law" },
          ]);
        }
      })
      .catch(() => { /* keep defaults */ });
  }, []);

  const update = (field) => (e) => {
    const val = e?.target ? e.target.value : e;
    setFormData(prev => ({ ...prev, [field]: val }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.username || !formData.password || !formData.email) {
      setError('Username, email and password are required');
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    if (!agreedTerms) {
      setError('Please agree to Terms and Conditions');
      return;
    }

    setLoading(true);
    try {
      await authAPI.register({
        username: formData.username,
        password: formData.password,
        email: formData.email,
      });
      navigate('/', { state: { registered: true } });
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Username may already exist.');
      setLoading(false);
    }
  };

  const InputField = ({ label, id, type = 'text', placeholder, value, onChange, required, children }) => (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-muted-foreground dark:text-muted-foreground mb-1.5">
        {label} {required && <span className="text-red-400">*</span>}
      </label>
      {children || (
        <input
          id={id}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className="w-full px-4 py-2.5 bg-white dark:bg-background border border-muted dark:border-border rounded-lg text-slate-900 dark:text-foreground placeholder-slate-400 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all"
          data-testid={`register-${id}-input`}
        />
      )}
    </div>
  );

  return (
    <div className="min-h-screen flex" data-testid="register-page">
      {/* Left Panel — Brand */}
      <div className="hidden lg:flex lg:w-[48%] relative overflow-hidden bg-[#022419]">
        <div className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />
        <div className="relative z-10 flex flex-col justify-between p-12 xl:p-16 w-full">
          <div>
            <Link to="/" className="flex items-baseline gap-0.5 mb-1 hover:opacity-80 transition-opacity">
              <span className="text-emerald-400 text-3xl xl:text-4xl font-bold tracking-tight font-serif">Pakistan</span>
              <span className="text-primary-foreground text-3xl xl:text-4xl font-bold tracking-tight font-serif">LawApp</span>
            </Link>
            <div className="h-0.5 w-16 bg-[#B4914A] mt-2" />
          </div>

          <div className="my-auto py-8">
            <h1 className="text-primary-foreground text-4xl xl:text-5xl font-serif font-bold leading-tight mb-6 tracking-tight">
              Join Pakistan's<br />
              <span className="text-emerald-400">Legal Research</span><br />
              Community
            </h1>
            <p className="text-muted-foreground text-lg leading-relaxed max-w-lg mb-10">
              Create your account to access the most comprehensive collection of Pakistani case laws, statutes, and AI-powered legal research tools.
            </p>

            <div className="grid grid-cols-2 gap-6 mb-10">
              {stats.map((stat) => (
                <div key={stat.label}>
                  <div className="text-[#B4914A] text-2xl font-bold font-mono">{stat.value}</div>
                  <div className="text-muted-foreground dark:text-muted-foreground text-xs mt-1 uppercase tracking-wider">{stat.label}</div>
                </div>
              ))}
            </div>

            <div className="space-y-3">
              {[
                { icon: Search, text: 'Full-text search across 194k+ judgments' },
                { icon: Scale, text: 'AI-powered case analysis and summaries' },
                { icon: Shield, text: 'Court performance analytics' },
              ].map((f, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
                    <f.icon size={16} className="text-emerald-400" />
                  </div>
                  <span className="text-muted-foreground text-sm">{f.text}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="text-foreground dark:text-muted-foreground text-xs">Powered by PLD Publishers</div>
        </div>
      </div>

      {/* Right Panel — Register Form */}
      <div className="flex-1 flex items-start justify-center bg-background px-6 py-8 sm:px-12 overflow-y-auto">
        <div className="w-full max-w-lg">
          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-6">
            <Link to="/" className="inline-flex items-baseline gap-0.5">
              <span className="text-primary dark:text-primary text-2xl font-bold font-serif">Pakistan</span>
              <span className="text-slate-800 dark:text-foreground text-2xl font-bold font-serif">LawApp</span>
            </Link>
          </div>

          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-serif font-bold text-slate-900 dark:text-foreground" data-testid="register-title">
                Create Account
              </h2>
              <p className="text-muted-foreground dark:text-muted-foreground text-sm mt-1">Join thousands of legal professionals</p>
            </div>
            <Link to="/" className="text-sm text-emerald-600 hover:text-primary dark:text-primary flex items-center gap-1" data-testid="back-to-login-link">
              <ArrowLeft size={14} /> Sign in
            </Link>
          </div>

          <form onSubmit={handleRegister} className="space-y-4" data-testid="register-form">
            <div className="grid grid-cols-2 gap-4">
              <InputField label="First Name" id="firstName" placeholder="First name" value={formData.firstName} onChange={update('firstName')} />
              <InputField label="Last Name" id="lastName" placeholder="Last name" value={formData.lastName} onChange={update('lastName')} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <InputField label="Email" id="email" type="email" placeholder="you@example.com" value={formData.email} onChange={update('email')} required />
              <InputField label="Phone" id="phone" placeholder="+92-xxx-xxxxxxx" value={formData.phone} onChange={update('phone')} />
            </div>

            <InputField label="Username" id="username" placeholder="Choose a username (min 4 characters)" value={formData.username} onChange={update('username')} required />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-muted-foreground dark:text-muted-foreground mb-1.5">
                  Password <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Min 6 characters"
                    value={formData.password}
                    onChange={update('password')}
                    className="w-full px-4 py-2.5 bg-white dark:bg-background border border-muted dark:border-border rounded-lg text-slate-900 dark:text-foreground placeholder-slate-400 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 pr-11 transition-all"
                    data-testid="register-password-input"
                  />
                  <button type="button" onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground dark:text-muted-foreground" tabIndex={-1}>
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
              <InputField label="Confirm Password" id="confirmPassword" type="password" placeholder="Re-enter password" value={formData.confirmPassword} onChange={update('confirmPassword')} required />
            </div>

            <InputField label="Address" id="address" placeholder="Your address" value={formData.address} onChange={update('address')} />

            <div className="grid grid-cols-2 gap-4">
              <InputField label="Country" id="country" required>
                <Select value={formData.country} onValueChange={update('country')}>
                  <SelectTrigger data-testid="register-country-select" className="bg-white dark:bg-background border-muted dark:border-border">
                    <SelectValue placeholder="Select country" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pakistan">Pakistan</SelectItem>
                    <SelectItem value="uk">United Kingdom</SelectItem>
                    <SelectItem value="usa">United States</SelectItem>
                    <SelectItem value="uae">UAE</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </InputField>
              <InputField label="Profession" id="profession">
                <Select value={formData.profession} onValueChange={update('profession')}>
                  <SelectTrigger data-testid="register-profession-select" className="bg-white dark:bg-background border-muted dark:border-border">
                    <SelectValue placeholder="Select profession" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="advocate">Advocate</SelectItem>
                    <SelectItem value="judge">Judge</SelectItem>
                    <SelectItem value="student">Law Student</SelectItem>
                    <SelectItem value="academic">Academic</SelectItem>
                    <SelectItem value="corporate">Corporate Lawyer</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </InputField>
              <InputField label="City" id="city" placeholder="Your city" value={formData.city} onChange={update('city')} />
            </div>

            <div className="flex items-start gap-2.5 pt-1">
              <Checkbox
                id="reg-terms"
                checked={agreedTerms}
                onCheckedChange={setAgreedTerms}
                data-testid="register-terms-checkbox"
                className="mt-0.5 data-[state=checked]:bg-emerald-600 data-[state=checked]:border-emerald-600"
              />
              <label htmlFor="reg-terms" className="text-sm text-foreground dark:text-muted-foreground leading-tight cursor-pointer select-none">
                I agree to the{' '}
                <Link to="/terms" className="text-emerald-600 hover:text-primary dark:text-primary underline underline-offset-2">
                  Terms & Conditions
                </Link>
              </label>
            </div>

            {error && (
              <div className="bg-red-50 text-red-600 text-sm px-4 py-2.5 rounded-lg border border-red-100" data-testid="register-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-[#044732] hover:bg-[#033825] text-primary-foreground font-medium rounded-lg transition-all duration-200 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed shadow-sm"
              data-testid="register-submit-btn"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : <>Create Account <ArrowRight size={16} /></>}
            </button>

            <p className="text-center text-sm text-muted-foreground dark:text-muted-foreground pt-2">
              Already have an account?{' '}
              <Link to="/" className="text-emerald-600 hover:text-primary dark:text-primary font-medium underline underline-offset-2" data-testid="login-link">
                Sign in
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
