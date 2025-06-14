/****************************************************************************
 *
 *   Copyright (c) 2020 PX4 Development Team. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 * 3. Neither the name PX4 nor the names of its contributors may be
 *    used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 * OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 ****************************************************************************/

#include "Common.hpp"
#include "../ModeUtil/mode_requirements.hpp"

void Report::getHealthReport(health_report_s &report) const
{
    report.can_arm_mode_flags = 0xFFFFFFFFFFFFFFFF; // Tüm modlarda arming'e izin ver
    report.can_run_mode_flags = 0xFFFFFFFFFFFFFFFF; // Tüm modlarda çalıştırmaya izin ver
    report.arming_check_error_flags = 0; // Hata bayraklarını sıfırla
    report.arming_check_warning_flags = 0; // Uyarı bayraklarını sıfırla
    report.health_is_present_flags = 0xFFFFFFFFFFFFFFFF; // Tüm bileşenleri mevcut olarak işaretle
    report.health_error_flags = 0; // Sağlık hatalarını sıfırla
    report.health_warning_flags = 0; // Sağlık uyarılarını sıfırla
}

void Report::healthFailure(NavModes required_modes, HealthComponentIndex component, uint32_t event_id,
                          const events::LogLevels &log_levels, const char *message)
{
    // Sağlık hatalarını raporlama, hiçbir işlem yapma
    return;
}

void Report::armingCheckFailure(NavModes required_modes, HealthComponentIndex component, uint32_t event_id,
                               const events::LogLevels &log_levels, const char *message)
{
    // Arming hatalarını raporlama, hiçbir işlem yapma
    return;
}

void Report::armingCheckFailure(NavModesMessageFail required_modes, HealthComponentIndex component,
                               uint32_t event_id, const events::LogLevels &log_levels, const char *message)
{
    // Arming hatalarını raporlama, hiçbir işlem yapma
    return;
}

Report::EventBufferHeader *Report::addEventToBuffer(uint32_t event_id, const events::LogLevels &log_levels,
                                                   uint32_t modes, unsigned args_size)
{
    // Olayları kaydetme, doğrudan nullptr döndür
    return nullptr;
}

bool Report::addExternalEvent(const event_s &event, NavModes modes)
{
    // Dış olayları kaydetme
    return false;
}

NavModes Report::reportedModes(NavModes required_modes)
{
    // Tüm modları destekle
    return NavModes::All;
}

void Report::setIsPresent(health_component_t component)
{
    // Tüm bileşenleri mevcut olarak işaretle
    HealthResults &health = _results[_current_result].health;
    health.is_present = health.is_present | component;
}

void Report::setHealth(health_component_t component, bool is_present, bool warning, bool error)
{
    // Sağlık durumunu güncelleme, hataları ve uyarıları yoksay
    HealthResults &health = _results[_current_result].health;
    if (is_present) {
        health.is_present = health.is_present | component;
    }
    // Uyarı ve hata bayraklarını ayarlamayı yoksay
}

void Report::healthFailure(NavModes required_modes, HealthComponentIndex component, events::Log log_level)
{
    // Sağlık hatalarını raporlama
    return;
}

void Report::armingCheckFailure(NavModes required_modes, HealthComponentIndex component, events::Log log_level)
{
    // Arming hatalarını raporlama
    return;
}

void Report::clearArmingBits(NavModes modes)
{
    // Arming bitlerini temizlemeyi yoksay
}

void Report::clearCanRunBits(NavModes modes)
{
    // Çalıştırma bitlerini temizlemeyi yoksay
}

void Report::reset()
{
    _current_result = (_current_result + 1) % 2;
    _results[_current_result].reset();
    _next_buffer_idx = 0;
    _buffer_overflowed = false;
    _results_changed = false;
}

void Report::prepare(uint8_t vehicle_type)
{
    // Mod gereksinimlerini tüm modlar için geçerli yap
    _failsafe_flags.angular_velocity_invalid = false;
    _failsafe_flags.attitude_invalid = false;
    _failsafe_flags.local_altitude_invalid = false;
    _failsafe_flags.local_position_invalid = false;
    _failsafe_flags.local_position_invalid_relaxed = false;
    _failsafe_flags.local_velocity_invalid = false;
    _failsafe_flags.global_position_invalid = false;
    _failsafe_flags.auto_mission_missing = false;
    _failsafe_flags.offboard_control_signal_lost = false;
    _failsafe_flags.home_position_invalid = false;
}

NavModes Report::getModeGroup(uint8_t nav_state) const
{
    // Tüm navigasyon modlarını destekle
    return NavModes::All;
}

bool Report::finalize()
{
    _results[_current_result].arming_checks.valid = true;
    _already_reported = false;
    _results_changed = false; // Değişiklikleri yoksay
    return false; // Raporlamayı engelle
}

bool Report::report(bool force)
{
    // Raporlamayı tamamen engelle
    return false;
}

bool Report::reportIfUnreportedDifferences()
{
    // Farklılıkları raporlama
    return false;
}

