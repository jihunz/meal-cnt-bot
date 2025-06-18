"""
주간 식사 인원 계산 테스트 서비스
현재 주의 월요일부터 금요일까지 식사 인원 계산 로직을 순차적으로 테스트합니다.
"""

from services.meal_count_service import MealCountService
from utils.date_util import DateUtil


class WeeklyTestService:
    """주간 식사 인원 계산 테스트 서비스"""

    def __init__(self, config_file='config/config.json'):
        """주간 테스트 서비스 초기화"""
        self.meal_count_service = MealCountService(config_file)

    def run_weekly_test(self):
        """주간 테스트 실행 - 월요일부터 금요일까지 순차적으로 테스트"""
        print(f'[{DateUtil.get_now()}] ==================== 주간 식사 인원 계산 테스트 시작 ====================')
        
        # 현재 주의 평일 날짜들 가져오기
        weekdays = DateUtil.get_current_week_dates()
        day_names = ['월요일', '화요일', '수요일', '목요일', '금요일']
        
        test_results = []
        
        for i, date in enumerate(weekdays):
            day_name = day_names[i]
            date_str = date.strftime("%Y-%m-%d")
            
            print(f'\n[{DateUtil.get_now()}] === {day_name} ({date_str}) 테스트 시작 ===')
            
            try:
                # 해당 날짜의 식사 인원 계산 로직 실행
                result = self.meal_count_service.process_meal_count(target_date=date)
                
                if result is None:
                    print(f'[{DateUtil.get_now()}] {day_name} ({date_str}): 식사 인원 계산 불가 (공휴일/워크샵 등)')
                    test_results.append({
                        'date': date_str,
                        'day_name': day_name,
                        'status': 'skipped',
                        'reason': '공휴일/워크샵 등으로 인한 제외'
                    })
                else:
                    print(f'[{DateUtil.get_now()}] {day_name} ({date_str}): 식사 인원 {result.count}명')
                    test_results.append({
                        'date': date_str,
                        'day_name': day_name,
                        'status': 'calculated',
                        'count': result.count,
                        'included_people': result.included_people,
                        'excluded_people': result.excluded_people,
                        'default_count': result.default_count
                    })
                    
            except Exception as e:
                print(f'[{DateUtil.get_now()}] {day_name} ({date_str}): 오류 발생 - {str(e)}')
                test_results.append({
                    'date': date_str,
                    'day_name': day_name,
                    'status': 'error',
                    'error': str(e)
                })
            
            print(f'[{DateUtil.get_now()}] === {day_name} ({date_str}) 테스트 완료 ===')
        
        # 테스트 결과 요약 출력
        self._print_test_summary(test_results)
        
        print(f'[{DateUtil.get_now()}] ==================== 주간 식사 인원 계산 테스트 완료 ====================')
        
        return test_results

    def _print_test_summary(self, test_results):
        """테스트 결과 요약 출력"""
        print(f'\n[{DateUtil.get_now()}] ==================== 주간 테스트 결과 요약 ====================')
        
        total_days = len(test_results)
        calculated_days = len([r for r in test_results if r['status'] == 'calculated'])
        skipped_days = len([r for r in test_results if r['status'] == 'skipped'])
        error_days = len([r for r in test_results if r['status'] == 'error'])
        
        print(f'[{DateUtil.get_now()}] 총 테스트 일수: {total_days}일')
        print(f'[{DateUtil.get_now()}] 계산 완료: {calculated_days}일')
        print(f'[{DateUtil.get_now()}] 제외된 날: {skipped_days}일')
        print(f'[{DateUtil.get_now()}] 오류 발생: {error_days}일')
        
        # 각 날짜별 상세 결과
        for result in test_results:
            if result['status'] == 'calculated':
                print(f'[{DateUtil.get_now()}] {result["day_name"]} ({result["date"]}): {result["count"]}명')
            elif result['status'] == 'skipped':
                print(f'[{DateUtil.get_now()}] {result["day_name"]} ({result["date"]}): 제외 - {result["reason"]}')
            elif result['status'] == 'error':
                print(f'[{DateUtil.get_now()}] {result["day_name"]} ({result["date"]}): 오류 - {result["error"]}')
        
        print(f'[{DateUtil.get_now()}] ================================================================')

    def get_current_week_summary(self):
        """현재 주의 식사 인원 요약 정보 반환"""
        weekdays = DateUtil.get_current_week_dates()
        summary = {
            'week_start': weekdays[0].strftime("%Y-%m-%d"),
            'week_end': weekdays[-1].strftime("%Y-%m-%d"),
            'daily_counts': []
        }
        
        for date in weekdays:
            try:
                result = self.meal_count_service.process_meal_count(target_date=date)
                if result:
                    summary['daily_counts'].append({
                        'date': date.strftime("%Y-%m-%d"),
                        'count': result.count
                    })
                else:
                    summary['daily_counts'].append({
                        'date': date.strftime("%Y-%m-%d"),
                        'count': 0,
                        'note': '제외된 날'
                    })
            except Exception as e:
                summary['daily_counts'].append({
                    'date': date.strftime("%Y-%m-%d"),
                    'count': 0,
                    'error': str(e)
                })
        
        return summary 