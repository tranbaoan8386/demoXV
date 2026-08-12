import { useRef, useState } from 'react'

import { docApi } from '../../api/doc.api'
import { auditApi } from '../../api/audit.api'
import { useNavigate } from 'react-router-dom'
import { Button } from '../common/Button'
import { AlertBanner } from '../common/AlertBanner'
import { getApiErrorMessage } from '../../utils/api'

interface FileUploaderProps {
  onUploadSuccess?: () => void
}

const acceptedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
const acceptedLabel = 'PDF, DOC, DOCX, TXT'

export function FileUploader({ onUploadSuccess }: FileUploaderProps) {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [dragActive, setDragActive] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)

  const handleUpload = async (file: File) => {
    if (!acceptedTypes.includes(file.type)) {
      setError('Định dạng tệp không được hỗ trợ. Vui lòng chọn PDF, DOC, DOCX hoặc TXT.')
      return
    }

    setLoading(true)
    setError('')
    setUploadProgress(0)

    try {
      const resp = await docApi.uploadDocument(file, (progressEvent) => {
        if (progressEvent.total) {
          setUploadProgress(Math.min(100, Math.round((progressEvent.loaded / progressEvent.total) * 100)))
        }
      })
      const documentId = resp?.data?.data?.document_id
      // If we have a documentId, trigger audit automatically
      if (documentId) {
        try {
          await auditApi.createAudit({ document_id: documentId })
          // after audit created, refresh list and navigate to audit page
          onUploadSuccess?.()
          navigate(`/audit/${documentId}`)
        } catch (auditErr) {
          // If audit creation failed, still refresh list and surface error
          onUploadSuccess?.()
          setError(getApiErrorMessage(auditErr))
        }
      } else {
        onUploadSuccess?.()
      }
      setUploadProgress(100)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setLoading(false)
      window.setTimeout(() => setUploadProgress(0), 700)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    void handleUpload(file)
  }

  const handleDragEvents = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    event.stopPropagation()
    if (event.type === 'dragenter' || event.type === 'dragover') {
      setDragActive(true)
    } else {
      setDragActive(false)
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    event.stopPropagation()
    setDragActive(false)

    const file = event.dataTransfer.files?.[0]
    if (!file) return

    void handleUpload(file)
  }

  return (
    <div>
      <div
        className={`group rounded-[28px] border border-dashed bg-white/90 p-8 text-center transition ${
          dragActive ? 'border-brand-500 bg-brand-50/70 shadow-glow' : 'border-slate-200 hover:border-brand-300'
        }`}
        onDragEnter={handleDragEvents}
        onDragOver={handleDragEvents}
        onDragLeave={handleDragEvents}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileChange}
          className="hidden"
          disabled={loading}
        />
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-brand-500 text-white shadow-lg shadow-brand-500/20">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-8 w-8">
            <path d="M12 3.75a.75.75 0 01.75.75v7.69l2.72-2.72a.75.75 0 011.06 1.06l-4.24 4.25a.75.75 0 01-1.06 0L8.47 9.84a.75.75 0 111.06-1.06l2.72 2.72V4.5A.75.75 0 0112 3.75zm-7.5 12.75a.75.75 0 01.75-.75h3.75a.75.75 0 010 1.5H5.25a.75.75 0 01-.75-.75zm12 0a.75.75 0 01.75-.75h3.75a.75.75 0 010 1.5h-3.75a.75.75 0 01-.75-.75z" />
          </svg>
        </div>
        <div className="mt-6 space-y-3">
          <p className="text-xl font-semibold text-slate-900">Kéo thả tệp hoặc chọn tệp từ máy</p>
          <p className="text-sm text-slate-500">Hỗ trợ định dạng {acceptedLabel} | Tải lên nhanh chóng với audit AI.</p>
          <Button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            loading={loading}
            disabled={loading}
            className="mx-auto mt-2"
          >
            Chọn tệp
          </Button>
        </div>
      </div>

      {uploadProgress > 0 && (
        <div className="mt-4 overflow-hidden rounded-full bg-slate-200">
          <div
            className="h-2 rounded-full bg-brand-500 transition-all duration-300"
            style={{ width: `${uploadProgress}%` }}
          />
        </div>
      )}

      {error && <AlertBanner type="error" message={error} className="mt-4" />}
    </div>
  )
}
