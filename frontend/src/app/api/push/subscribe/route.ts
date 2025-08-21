import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { subscription } = body;

    if (!subscription) {
      return NextResponse.json(
        { error: 'Subscription object is required' },
        { status: 400 }
      );
    }

    // TODO: 실제 데이터베이스에 구독 정보 저장
    // const savedSubscription = await saveSubscriptionToDatabase(subscription);

    // TODO: 실제 푸시 알림 서비스로 전송
    // await sendPushNotification(subscription, {
    //   title: 'GreenSteel 알림',
    //   body: '푸시 알림이 활성화되었습니다!',
    //   icon: '/icon-192x192.png',
    // });

    return NextResponse.json({
      success: true,
      message: 'Push notification subscription successful',
      subscription: {
        endpoint: subscription.endpoint,
        keys: subscription.keys,
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to process subscription' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { userId } = await request.json();

    if (!userId) {
      return NextResponse.json({ error: 'Missing userId' }, { status: 400 });
    }

    // TODO: 실제 데이터베이스에서 구독 정보 삭제
    // await deleteSubscriptionFromDatabase(userId);

    return NextResponse.json({
      success: true,
      message: 'Push notification unsubscription successful',
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
