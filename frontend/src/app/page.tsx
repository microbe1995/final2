// ============================================================================
// 🏠 홈페이지 컴포넌트
// ============================================================================

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-6">
            CBAM Calculator에 오신 것을 환영합니다! 🎉
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            사용자 계정 관리 시스템을 통해 안전하고 편리하게 서비스를 이용하세요.
            회원가입 후 로그인하여 개인화된 서비스를 경험해보세요.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/register"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
            >
              🚀 회원가입하기
            </a>
            
            <a
              href="/login"
              className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
            >
              🔐 로그인하기
            </a>
          </div>
          
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-4">👤</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">간편한 회원가입</h3>
              <p className="text-gray-600">
                한글 사용자명을 지원하는 간편한 회원가입으로 빠르게 시작하세요.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-4">🔒</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">안전한 인증</h3>
              <p className="text-gray-600">
                SHA256 해싱을 통한 안전한 비밀번호 관리로 계정을 보호합니다.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-4">💾</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">데이터 저장</h3>
              <p className="text-gray-600">
                PostgreSQL 데이터베이스에 안전하게 사용자 정보를 저장합니다.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 