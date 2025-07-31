import { NextRequest, NextResponse } from 'next/server';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

export async function POST(request: NextRequest) {
  try {
    const { name, email, password } = await request.json();

    // 입력 검증
    if (!name || !email || !password) {
      return NextResponse.json(
        { error: '모든 필드를 입력해주세요.' },
        { status: 400 }
      );
    }

    if (password.length < 6) {
      return NextResponse.json(
        { error: '비밀번호는 최소 6자 이상이어야 합니다.' },
        { status: 400 }
      );
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: '유효한 이메일 주소를 입력해주세요.' },
        { status: 400 }
      );
    }

    // 비밀번호 해싱
    const hashedPassword = await bcrypt.hash(password, 12);

    // JWT 토큰 생성
    const token = jwt.sign(
      { 
        userId: Date.now().toString(), // 실제로는 데이터베이스에서 생성된 ID 사용
        email,
        name 
      },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '7d' }
    );

    // 성공 응답
    return NextResponse.json({
      success: true,
      message: '회원가입이 완료되었습니다.',
      user: {
        id: Date.now().toString(),
        name,
        email
      },
      token
    });

  } catch (error) {
    console.error('Register error:', error);
    return NextResponse.json(
      { error: '서버 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
} 