import { motion } from 'framer-motion';

// Page wrapper — fade + slide up on route change
export const PageTransition = ({ children, className = '' }) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -8 }}
    transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
    className={className}
  >
    {children}
  </motion.div>
);

// Stagger container — children animate in sequence
export const StaggerContainer = ({ children, className = '', delay = 0 }) => (
  <motion.div
    initial="hidden"
    animate="visible"
    variants={{
      hidden: {},
      visible: {
        transition: {
          staggerChildren: 0.06,
          delayChildren: delay,
        },
      },
    }}
    className={className}
  >
    {children}
  </motion.div>
);

// Individual stagger item — used inside StaggerContainer
export const StaggerItem = ({ children, className = '' }) => (
  <motion.div
    variants={{
      hidden: { opacity: 0, y: 16 },
      visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] },
      },
    }}
    className={className}
  >
    {children}
  </motion.div>
);

// Fade in from bottom — standalone
export const FadeInUp = ({ children, className = '', delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4, delay, ease: [0.25, 0.1, 0.25, 1] }}
    className={className}
  >
    {children}
  </motion.div>
);

// Fade in from left
export const FadeInLeft = ({ children, className = '', delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ duration: 0.4, delay, ease: [0.25, 0.1, 0.25, 1] }}
    className={className}
  >
    {children}
  </motion.div>
);

// Scale in — for cards/modals
export const ScaleIn = ({ children, className = '', delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.3, delay, ease: [0.25, 0.1, 0.25, 1] }}
    className={className}
  >
    {children}
  </motion.div>
);

// Number counter — animates numbers counting up
export const AnimatedNumber = ({ value, className = '' }) => (
  <motion.span
    key={value}
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4, ease: 'easeOut' }}
    className={className}
  >
    {typeof value === 'number' ? value.toLocaleString() : value}
  </motion.span>
);

// Hover card wrapper — lift + shadow on hover
export const HoverCard = ({ children, className = '', onClick }) => (
  <motion.div
    whileHover={{ y: -2, boxShadow: '0 8px 25px -5px rgba(0,0,0,0.1), 0 4px 10px -6px rgba(0,0,0,0.1)' }}
    whileTap={{ scale: 0.985 }}
    transition={{ duration: 0.2, ease: 'easeOut' }}
    className={className}
    onClick={onClick}
  >
    {children}
  </motion.div>
);

// List item — for search results, table rows
export const ListItem = ({ children, className = '', index = 0 }) => (
  <motion.div
    initial={{ opacity: 0, x: -8 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ duration: 0.3, delay: index * 0.04, ease: [0.25, 0.1, 0.25, 1] }}
    className={className}
  >
    {children}
  </motion.div>
);
