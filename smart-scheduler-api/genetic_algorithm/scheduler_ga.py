# smart-scheduler-api/genetic_algorithm/scheduler_ga.py
import random
import numpy as np # Đảm bảo bạn đã import numpy

# ... (Toàn bộ code ScheduleGA và find_optimal_schedule của bạn ở đây) ...
# (Code bạn gửi đã rất tốt, giữ nguyên)
class ScheduleGA:
    def __init__(self, subjects, time_slots, constraints, priorities=None, additional_constraints=None, subject_details=None):
        self.subjects = subjects
        self.time_slots = time_slots
        self.constraints = constraints # Ví dụ: {'Toán': ['Thứ 2 - Sáng']}
        self.priorities = priorities or {}  # Dictionary: subject_name -> priority (1-10)
        self.additional_constraints = additional_constraints or {}  # Ràng buộc bổ sung
        self.subject_details = subject_details or {}
        
        self.num_subjects = len(subjects)
        self.num_slots = len(time_slots)

        # Tạo map để tra cứu index nhanh (rất quan trọng)
        self.slot_to_index = {slot: i for i, slot in enumerate(self.time_slots)}

    # === 1. BIỂU DIỄN (Chromosome) ===
    def create_individual(self):
        return [random.randint(0, self.num_slots - 1) for _ in range(self.num_subjects)]

    # === 2. HÀM THÍCH NGHI (Fitness Function) ===
    def calculate_fitness(self, individual):
        penalty = 0
        
        # Ràng buộc 1: Trùng lịch (Penalty 1000, nhưng ưu tiên môn có priority cao hơn)
        slots_used = {}  # slot_index -> list of subjects
        for i, slot_index in enumerate(individual):
            subject_name = self.subjects[i]
            if slot_index in slots_used:
                # Nếu trùng, ưu tiên môn có priority cao hơn
                existing_subject = slots_used[slot_index][0]
                current_priority = self.priorities.get(subject_name, 5)
                existing_priority = self.priorities.get(existing_subject, 5)
                
                if current_priority > existing_priority:
                    # Môn hiện tại có priority cao hơn, giữ lại
                    penalty += 1000  # Vẫn phạt nhưng ít hơn
                else:
                    # Môn hiện tại có priority thấp hơn, phạt nặng hơn
                    penalty += 1500
            else:
                slots_used[slot_index] = [subject_name]
            
        # Ràng buộc 2: Giờ cấm (Penalty 500, tăng theo priority thấp)
        for i, subject_name in enumerate(self.subjects):
            if subject_name in self.constraints:
                forbidden_slots = self.constraints[subject_name]
                
                assigned_slot_index = individual[i]
                assigned_slot_name = self.time_slots[assigned_slot_index]
                
                if assigned_slot_name in forbidden_slots:
                    priority = self.priorities.get(subject_name, 5)
                    # Môn có priority cao hơn bị phạt ít hơn khi vi phạm
                    penalty += 500 - (priority - 5) * 50

        # Ràng buộc 3: Tránh xếp các môn học liên tiếp
        if self.additional_constraints.get('avoidConsecutive', False):
            for i in range(len(individual) - 1):
                slot1 = self.time_slots[individual[i]]
                slot2 = self.time_slots[individual[i + 1]]
                # Kiểm tra nếu 2 môn liên tiếp cùng ngày
                day1 = slot1.split('_')[0]
                day2 = slot2.split('_')[0]
                if day1 == day2:
                    penalty += 200  # Phạt nhẹ nếu liên tiếp

        # Ràng buộc 4: Cân bằng số môn học giữa các ngày
        if self.additional_constraints.get('balanceDays', False):
            day_counts = {}
            for slot_index in individual:
                slot_name = self.time_slots[slot_index]
                day = slot_name.split('_')[0]
                day_counts[day] = day_counts.get(day, 0) + 1
            
            if day_counts:
                max_count = max(day_counts.values())
                min_count = min(day_counts.values())
                penalty += (max_count - min_count) * 50  # Phạt nếu chênh lệch nhiều

        # Ràng buộc 5: Ưu tiên học buổi sáng
        if self.additional_constraints.get('preferMorning', False):
            for i, slot_index in enumerate(individual):
                slot_name = self.time_slots[slot_index]
                if 'Chiều' in slot_name:
                    penalty += 100  # Phạt nhẹ nếu xếp buổi chiều

        # Ràng buộc 6: Cho phép học thứ 7
        if not self.additional_constraints.get('allowSaturday', False):
            for i, slot_index in enumerate(individual):
                slot_name = self.time_slots[slot_index]
                if 'T7' in slot_name:
                    penalty += 300  # Phạt nếu xếp thứ 7 khi không cho phép

        # Ràng buộc 7: Phạt khi xếp vào unavailable slots (ngày không rảnh)
        available_slots = self.additional_constraints.get('available_slots', [])
        unavailable_slots = self.additional_constraints.get('unavailable_slots', [])
        
        for i, slot_index in enumerate(individual):
            subject_name = self.subjects[i]
            slot_name = self.time_slots[slot_index]
            
            # Phạt nặng nếu xếp vào unavailable slot (nhưng vẫn cho phép)
            if slot_name in unavailable_slots:
                priority = self.priorities.get(subject_name, 5)
                # Phạt ít hơn nếu priority cao (cho phép môn quan trọng vào ngày không rảnh)
                penalty += 800 - (priority - 5) * 50
            
            # Thưởng khi xếp vào preferred_days
            preferred_days = self.subject_details.get(subject_name, {}).get("preferred_days", [])
            if preferred_days:
                day = slot_name.split('_')[0]
                if day in preferred_days:
                    # Thưởng (giảm penalty) khi xếp đúng ngày ưu tiên
                    penalty -= 150
            
            is_retake = self.subject_details.get(subject_name, {}).get("is_retake", False)
            if not is_retake and "Tối" in slot_name:
                penalty += 80  # Giảm xếp lớp thường vào buổi tối
            if is_retake and "Sáng" in slot_name:
                penalty -= 20  # Khuyến khích môn học lại lên buổi sáng sớm để ưu tiên

        return penalty

    # === 3. CHỌN LỌC (Selection) ===
    def selection(self, population_with_scores):
        tournament_size = 5
        tournament = random.sample(population_with_scores, tournament_size)
        tournament.sort(key=lambda x: x[1]) # x[1] là điểm penalty
        return tournament[0][0], tournament[1][0] # x[0] là cá thể (list)

    # === 4. LAI GHÉP (Crossover) ===
    def crossover(self, parent1, parent2):
        point = random.randint(1, self.num_subjects - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    # === 5. ĐỘT BIẾN (Mutation) ===
    def mutate(self, individual):
        if random.random() < 0.1: # Tỷ lệ đột biến 10%
            subject_index = random.randint(0, self.num_subjects - 1)
            new_slot_index = random.randint(0, self.num_slots - 1)
            individual[subject_index] = new_slot_index
        return individual

    # ----------------------------------------------------
    # HÀM CHẠY CHÍNH
    # ----------------------------------------------------
    def run_ga(self):
        POPULATION_SIZE = 100
        GENERATIONS = 200 # Số thế hệ

        population = [self.create_individual() for _ in range(POPULATION_SIZE)]
        best_individual = None
        best_score = float('inf')

        for gen in range(GENERATIONS):
            population_with_scores = []
            for individual in population:
                score = self.calculate_fitness(individual)
                population_with_scores.append((individual, score))
                
                if score < best_score:
                    best_score = score
                    best_individual = individual

            if best_score == 0:
                print("Tìm thấy giải pháp hoàn hảo!")
                break
                
            new_population = []
            population_with_scores.sort(key=lambda x: x[1])
            elitism_count = int(POPULATION_SIZE * 0.1)
            new_population.extend([ind[0] for ind in population_with_scores[:elitism_count]])

            while len(new_population) < POPULATION_SIZE:
                parent1, parent2 = self.selection(population_with_scores)
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.append(child1)
                if len(new_population) < POPULATION_SIZE:
                    new_population.append(child2)

            population = new_population
            
            if gen % 20 == 0:
                print(f"Thế hệ {gen}: Điểm tốt nhất (penalty) = {best_score}")

        print(f"Hoàn tất GA! Điểm cuối cùng = {best_score}")
        
        return self.decode_result(best_individual), best_score

    def decode_result(self, best_individual):
        schedule_result = []
        for i, subject_name in enumerate(self.subjects):
            slot_index = best_individual[i]
            slot_name = self.time_slots[slot_index]
            schedule_result.append({
                "subject": subject_name,
                "time": slot_name
            })
        return schedule_result

# ----------------------------------------------------
# HÀM "CÔNG KHAI" ĐỂ main.py GỌI
# ----------------------------------------------------
def find_optimal_schedule(subjects, time_slots, constraints, priorities=None, additional_constraints=None, subject_details=None):
    ga = ScheduleGA(subjects, time_slots, constraints, priorities, additional_constraints, subject_details)
    final_schedule, final_cost = ga.run_ga()
    return final_schedule, final_cost