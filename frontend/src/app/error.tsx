'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-ecotrace-background">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-ecotrace-text mb-4">500</h1>
        <h2 className="text-2xl font-semibold text-ecotrace-textSecondary mb-4">
          서버 오류가 발생했습니다
        </h2>
        <p className="text-ecotrace-textSecondary mb-8">
          죄송합니다. 서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.
        </p>
        <div className="space-x-4">
          <button
            onClick={reset}
            className="inline-flex items-center px-6 py-3 bg-ecotrace-primary text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            다시 시도
          </button>
          <a
            href="/"
            className="inline-flex items-center px-6 py-3 bg-ecotrace-surface text-ecotrace-text border border-ecotrace-border rounded-lg hover:bg-ecotrace-border transition-colors"
          >
            홈으로 돌아가기
          </a>
        </div>
      </div>
    </div>
  );
}
