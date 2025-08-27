'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center bg-ecotrace-background">
          <div className="text-center">
            <h1 className="text-6xl font-bold text-ecotrace-text mb-4">오류</h1>
            <h2 className="text-2xl font-semibold text-ecotrace-textSecondary mb-4">
              예상치 못한 오류가 발생했습니다
            </h2>
            <p className="text-ecotrace-textSecondary mb-8">
              애플리케이션에서 오류가 발생했습니다. 페이지를 새로고침해주세요.
            </p>
            <button
              onClick={reset}
              className="inline-flex items-center px-6 py-3 bg-ecotrace-primary text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              다시 시도
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
