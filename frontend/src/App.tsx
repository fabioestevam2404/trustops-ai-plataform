import { Route, Routes } from 'react-router-dom'
import { AssessmentDetailPage } from './pages/AssessmentDetailPage'
import { ProjectDetailPage } from './pages/ProjectDetailPage'
import { ProjectListPage } from './pages/ProjectListPage'

export function App() {
  return (
    <Routes>
      <Route path="/" element={<ProjectListPage />} />
      <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
      <Route path="/assessments/:assessmentId" element={<AssessmentDetailPage />} />
    </Routes>
  )
}
