import json
from datetime import datetime
from typing import List, Optional, Dict, Any

FILE_NAME = 'piggy_bank.json'

class Goal:
    def __init__(self, name: str, target_amount: float, category: str, status: str = 'активна'):
        self.name = name
        self.target_amount = target_amount
        self.current_balance = 0.0
        self.category = category
        self.status = status
        self.history: List[Dict[str, Any]] = []

    def add_to_balance(self, amount: float) -> bool:
        if amount < 0:
            return False
        new_balance = self.current_balance + amount
        if new_balance > self.target_amount:
            new_balance = self.target_amount
        diff = new_balance - self.current_balance
        self.current_balance = new_balance
        self._log_change('Пополнение', diff)
        self._check_completion()
        return True

    def subtract_from_balance(self, amount: float) -> bool:
        if amount < 0 or amount > self.current_balance:
            return False
        self.current_balance -= amount
        self._log_change('снятие', -amount)
        return True

    def _check_completion(self):
        if self.current_balance >= self.target_amount and self.status != 'выполнена':
            self.status = 'выполнена'
            self._log_change('статус', 'выполнена')

    def _log_change(self, change_type: str, value: Any):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': change_type,
            'value': value,
            'balance_after': self.current_balance,
        }
        self.history.append(entry)

    @property
    def progress_percent(self) -> float:
        if self.target_amount == 0:
            return 0.0
        return round((self.current_balance / self.target_amount) * 100, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'target_amount': self.target_amount,
            'current_balance': self.current_balance,
            'category': self.category,
            'status': self.status,
            'history': self.history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Goal':
        goal = cls(
            name=data['name'],
            target_amount=data['target_amount'],
            category=data['category'],
            status=data.get('status', 'активна'),
        )
        goal.current_balance = data.get('current_balance', 0.0)
        goal.history = data.get('history', [])
        goal._check_completion()
        return goal

class PiggyBank:
    CATEGORIES = ['Работа', 'Здоровье', 'Путешествия', 'Техника', 'Образование', 'Другое']

    def __init__(self):
        self.goals: List[Goal] = []
        self.load_data()

    def load_data(self):
        try:
            with open(FILE_NAME, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.goals = [Goal.from_dict(g) for g in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.goals = []

    def save_data(self):
        with open(FILE_NAME, 'w', encoding='utf-8') as f:
            json.dump([g.to_dict() for g in self.goals], f, ensure_ascii=False, indent=2)

    def add_goal(self, name: str, target_amount: float, category: str) -> bool:
        if any(g.name == name for g in self.goals):
            return False
        goal = Goal(name, target_amount, category)
        self.goals.append(goal)
        self.save_data()
        return True

    def get_goal_by_name(self, name: str) -> Optional[Goal]:
        for g in self.goals:
            if g.name == name:
                return g
        return None

    def update_balance(self, goal_name: str, amount: float, is_addition: bool) -> bool:
        goal = self.get_goal_by_name(goal_name)
        if not goal:
            return False
        if is_addition:
            success = goal.add_to_balance(amount)
        else:
            success = goal.subtract_from_balance(amount)
        if success:
            self.save_data()
        return success

    def change_status(self, goal_name: str, new_status: str) -> bool:
        goal = self.get_goal_by_name(goal_name)
        if not goal:
            return False
        goal.status = new_status
        goal._log_change('статус', new_status)
        self.save_data()
        return True

    def delete_goal(self, goal_name: str) -> bool:
        goal = self.get_goal_by_name(goal_name)
        if not goal:
            return False
        self.goals.remove(goal)
        self.save_data()
        return True

    def overall_progress(self) -> float:
        total_target = sum(g.target_amount for g in self.goals)
        total_current = sum(g.current_balance for g in self.goals)
        if total_target == 0:
            return 0.0
        return round((total_current / total_target) * 100, 2)

    def check_threshold_notifications(self, threshold: float = 50.0) -> List[str]:
        notifications = []
        for goal in self.goals:
            if goal.progress_percent >= threshold and goal.status != 'выполнена':
                notifications.append(f"Цель '{goal.name}' достигла {goal.progress_percent}% прогресса!")
        return notifications

def get_float_input(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print('Сумма не может быть отрицательной. Попробуйте снова')
                continue
            return value
        except ValueError:
            print('Некорректный ввод. Введите число')

def main():
    piggy = PiggyBank()
    while True:
        print('\n--- Копилка ---')
        print('1. Добавить цель')
        print('2. Пополнить/снять с цели')
        print('3. Изменить статус цели')
        print('4. Удалить цель')
        print('5. Показать все цели и прогресс')
        print('6. Общий прогресс по всем целям')
        print('7. Проверить уведомления (порог 50%)')
        print('8. Выход')
        choice = input('Выберите действие: ').strip()

        if choice == '1':
            name = input('Название цели: ').strip()
            if not name:
                print('Название не может быть пустым.')
                continue
            target = get_float_input('Целевая сумма: ')
            print(f'Доступные категории: {', '.join(PiggyBank.CATEGORIES)}')
            category = input('Категория: ').strip()
            category_normalized = category.capitalize()
            if category_normalized not in PiggyBank.CATEGORIES:
                category_normalized = 'Другое'
                print(f"Категория не найдена, установите как '{category_normalized}'.")
            category = category_normalized
            if piggy.add_goal(name, target, category):
                print('Цель успешно добавлена.')
            else:
                print('Цель с таким названием уже существует.')

        elif choice == '2':
            goal_name = input('Название цели: ').strip()
            goal = piggy.get_goal_by_name(goal_name)
            if not goal:
                print('Цель не найдена.')
                continue
            print(f'Текущий баланс: {goal.current_balance}, цель: {goal.target_amount}')
            op = input('Пополнить (1) или снять (2)? ').strip()
            amount = get_float_input('Сумма: ')
            if op == '1':
                if piggy.update_balance(goal_name, amount, is_addition=True):
                    print('Баланс пополнен.')
                else:
                    print('Ошибка пополнения (возможно, превышена цель).')
            elif op == '2':
                if piggy.update_balance(goal_name, amount, is_addition=False):
                    print('Средства сняты.')
                else:
                    print('Ошибка: недостаточно средств или неверная сумма.')
            else:
                print('Неверная операция.')

        elif choice == '3':
            goal_name = input('Название цели: ').strip()
            new_status = input('Новый статус (например, активна/выполнена): ').strip()
            if piggy.change_status(goal_name, new_status):
                print('Статус обновлен.')
            else:
                print('Цель не найдена.')

        elif choice == '4':
            goal_name = input('Название цели для удаления: ').strip()
            if piggy.delete_goal(goal_name):
                print('Цель удалена.')
            else:
                print('Цель не найдена.')

        elif choice == '5':
            if not piggy.goals:
                print('Нет целей.')
                continue
            for g in piggy.goals:
                print(
                    f'{g.name}| Категория: {g.category}|'
                    f'Прогресс: {g.progress_percent}% ({g.current_balance}/{g.target_amount})'
                    f'Статус: {g.status}'
                )

        elif choice == '6':
            print(f'Общий прогресс по всем целям: {piggy.overall_progress()}%')

        elif choice == '7':
            notifications = piggy.check_threshold_notifications(50.0)
            if notifications:
                for n in notifications:
                    print(n)
            else:
                print('Пока нет целей, достигших порога 50%.')

        elif choice == '8':
            print('До свидания!')
            break
        else:
            print('Неверный выбор, попробуйте снова.')


if __name__ == '__main__':
    main()