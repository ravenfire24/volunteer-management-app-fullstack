import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy, useState } from 'react';

const Login = lazy(() => import('./components/Login'));
const Register = lazy(() => import('./components/Register'));
const ProfileForm = lazy(() => import('./components/ProfileForm'));
const VolunteerDash = lazy(() => import('./components/VolunteerDash'));
const AdminDash = lazy(() => import('./components/AdminDash'));
const VolunteerMatch = lazy(() => import('./components/VolunteerMatch'));
const VolunteerHistoryTable = lazy(() => import('./components/VolunteerHistory'));
const EventForm = lazy(() => import('./components/EventForm'));
const EventManagement = lazy(() => import('./components/EventManagement'));
const ViewAllEvents = lazy(() => import('./components/ViewAllEvents'));
const EventReview = lazy(() => import('./components/EventReview'));
const EventReport = lazy(() => import('./components/EventReport'));
const AllVolunteers = lazy(() => import('./components/AllVolunteers'));

function App() {
  const [users, setUsers] = useState([]); // Store registered users
  const [loggedInUser, setLoggedInUser] = useState(null);

  return (
    <Router>
      <Suspense fallback={<div className="route-loading">Loading...</div>}>
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/register" element={<Register users={users} setUsers={setUsers} />} />
          <Route path="/login" element={<Login users={users} setLoggedInUser={setLoggedInUser} />} />
          <Route path="/profile" element={<ProfileForm user={loggedInUser} />} />
          <Route path="/volunteerdash" element={<VolunteerDash />} />
          <Route path="/volunteermatch" element={<VolunteerMatch />} />
          <Route path="/admindash" element={<AdminDash />} />
          <Route path="/volunteerhistory" element={<VolunteerHistoryTable />} />
          <Route path="/events/create" element={<EventForm />} />
          <Route path="/eventmanagement" element={<EventManagement />} />
          <Route path="/viewallevents" element={<ViewAllEvents />} />
          <Route path="/events/edit/:eventId" element={<EventForm />} />
          <Route path="/eventreview" element={<EventReview />} />
          <Route path="/EventReview" element={<EventReview />} />
          <Route path="/eventreport" element={<EventReport />} />
          <Route path="/volunteers" element={<AllVolunteers />} />
        </Routes>
      </Suspense>
    </Router>
  );
}

export default App;
