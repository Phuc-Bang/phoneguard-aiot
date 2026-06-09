from sqlalchemy.orm import Session
from .. import crud, schemas, models

class Recommender:
    @staticmethod
    def generate_recommendations(db: Session, telemetry: schemas.TelemetryCreate) -> list:
        """
        Generates contextual recommendations based on current telemetry data.
        Returns a list of generated recommendations.
        """
        recs = []
        device_id = telemetry.device_id
        
        # 1. Low Battery Recommendation
        if telemetry.battery_level <= 20.0 and telemetry.battery_status.lower() in ["discharging", "not_charging"]:
            rec_create = schemas.RecommendationBase(
                device_id=device_id,
                title="Bật tiết kiệm pin",
                content="Dung lượng pin hiện tại là {:.0f}%. Bạn nên bật chế độ Tiết kiệm pin, giảm độ sáng màn hình và tắt GPS/Bluetooth để duy trì thời gian hoạt động.".format(telemetry.battery_level),
                category="BATTERY"
            )
            recs.append(crud.create_recommendation(db, rec_create))
            
        # 2. Fully Charged but Still Charging
        if telemetry.battery_level >= 100.0 and telemetry.battery_status.lower() == "charging":
            rec_create = schemas.RecommendationBase(
                device_id=device_id,
                title="Rút sạc bảo vệ pin",
                content="Thiết bị đã sạc đầy 100% nhưng vẫn đang cắm sạc. Hãy rút nguồn sạc để tránh sạc nhồi liên tục gây chai pin và tăng nhiệt độ.",
                category="BATTERY"
            )
            recs.append(crud.create_recommendation(db, rec_create))
            
        # 3. Overheating during heavy load or charging
        if telemetry.battery_temperature >= 42.0:
            rec_create = schemas.RecommendationBase(
                device_id=device_id,
                title="Hạ nhiệt thiết bị ngay",
                content="Nhiệt độ pin rất cao ({:.1f}°C). Vui lòng tháo ốp lưng (nếu có), ngắt kết nối sạc, tắt các ứng dụng chạy ngầm và không sử dụng điện thoại cho đến khi nguội hẳn.".format(telemetry.battery_temperature),
                category="TEMPERATURE"
            )
            recs.append(crud.create_recommendation(db, rec_create))
        elif telemetry.battery_temperature >= 38.0 and telemetry.battery_status.lower() == "charging":
            rec_create = schemas.RecommendationBase(
                device_id=device_id,
                title="Không vừa sạc vừa dùng",
                content="Nhiệt độ pin tăng lên {:.1f}°C khi đang sạc. Tránh việc chơi game, xem video hoặc chạy các ứng dụng nặng trong khi cắm sạc để ngăn nhiệt độ tăng thêm.".format(telemetry.battery_temperature),
                category="TEMPERATURE"
            )
            recs.append(crud.create_recommendation(db, rec_create))

        # 4. Network Signal Issues
        if telemetry.network_type.lower() == "cellular" and telemetry.network_strength is not None and telemetry.network_strength < -100.0:
            rec_create = schemas.RecommendationBase(
                device_id=device_id,
                title="Tín hiệu mạng di động yếu",
                content="Sóng di động yếu ({:.0f} dBm) khiến điện thoại phải tốn nhiều năng lượng hơn để duy trì kết nối. Hãy kết nối Wi-Fi hoặc di chuyển đến vùng sóng tốt hơn.".format(telemetry.network_strength),
                category="USAGE"
            )
            recs.append(crud.create_recommendation(db, rec_create))

        # 5. Clean up old recommendations, keep only the latest 5
        crud.clear_old_recommendations(db, device_id, keep_limit=5)
        
        return [r for r in recs if r is not None]
