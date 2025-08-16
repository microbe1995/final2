// ============================================================================
// 🏠 홈페이지 컴포넌트
// ============================================================================

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-200">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6 leading-tight transition-colors duration-200">
              Welcome to CBAM Calculator
        </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed transition-colors duration-200">
              사업장의 데이터를 안전하고 편리하게 관리해 제품별 탄소배출량을 계산하세요.
              회원가입 후 로그인하여 서비스를 경험해보세요.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/register"
                className="btn btn-primary text-lg px-15 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
              >
                SignIn
              </a>
              
              <a
                href="/login"
                className="btn btn-secondary text-lg px-15 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
              >
                SignUp
              </a>
            </div>
          </div>
        </div>
        
        {/* 배경 장식 */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-0 left-1/4 w-72 h-72 bg-blue-200 dark:bg-blue-900/30 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
          <div className="absolute top-0 right-1/4 w-72 h-72 bg-purple-200 dark:bg-purple-900/30 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-1/3 w-72 h-72 bg-pink-200 dark:bg-blue-900/30 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4 transition-colors duration-200">
              주요 기능
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 transition-colors duration-200">
              CBAM Calculator가 제공하는 핵심 기능들을 소개합니다
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* 회원가입 기능 */}
            <div className="card group hover:shadow-2xl transition-all duration-300">
              <div className="text-center">
                <div className="w-20 h-20 bg-blue-100 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50 transition-colors duration-200">
                  <svg className="w-10 h-10 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 transition-colors duration-200">간편한 회원가입</h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed transition-colors duration-200">
                  한글 사용자명을 지원하는 간편한 회원가입으로 빠르게 시작하세요.
                  실시간 중복 체크로 안전하게 계정을 생성할 수 있습니다.
                </p>
              </div>
            </div>
            
            {/* 보안 기능 */}
            <div className="card group hover:shadow-2xl transition-all duration-300">
              <div className="text-center">
                <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:bg-green-200 dark:group-hover:bg-green-900/50 transition-colors duration-200">
                  <svg className="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 transition-colors duration-200">안전한 인증</h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed transition-colors duration-200">
                  SHA256 해싱을 통한 안전한 비밀번호 관리로 계정을 보호합니다.
                  세션 관리와 접근 제어로 보안을 강화했습니다.
                </p>
              </div>
            </div>
            
            {/* 데이터 저장 */}
            <div className="card group hover:shadow-2xl transition-all duration-300">
              <div className="text-center">
                <div className="w-20 h-20 bg-purple-100 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:bg-purple-200 dark:group-hover:bg-purple-900/50 transition-colors duration-200">
                  <svg className="w-10 h-10 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 transition-colors duration-200">데이터 저장</h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed transition-colors duration-200">
                  PostgreSQL 데이터베이스에 안전하게 사용자 정보를 저장합니다.
                  백업 및 복구 시스템으로 데이터 안정성을 보장합니다.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-white dark:bg-gray-800 transition-colors duration-200">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6 transition-colors duration-200">
            지금 바로 시작해보세요!
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 transition-colors duration-200">
            CBAM Calculator와 함께 안전하고 편리한 서비스를 경험해보세요.
            회원가입은 단 1분이면 완료됩니다.
          </p>
        
      </div>
      </section>
    </div>
  );
} 