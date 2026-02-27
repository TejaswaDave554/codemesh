"""Complex e-commerce system simulation for testing code analysis.

This module demonstrates a multi-layered architecture with deep call chains,
inheritance hierarchies, and complex dependencies.
"""

from typing import List, Dict, Optional
import json


class DatabaseConnection:
    """Base database connection handler."""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.connected = False
    
    def connect(self):
        """Establish database connection."""
        self.connected = True
        return self.connected
    
    def disconnect(self):
        """Close database connection."""
        self.connected = False
    
    def execute_query(self, query: str):
        """Execute a database query."""
        if not self.connected:
            self.connect()
        return f"Executed: {query}"


class CacheManager:
    """Manages caching layer for performance."""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str):
        """Retrieve value from cache."""
        return self.cache.get(key)
    
    def set(self, key: str, value):
        """Store value in cache."""
        self.cache[key] = value
    
    def invalidate(self, key: str):
        """Remove value from cache."""
        if key in self.cache:
            del self.cache[key]
    
    def clear_all(self):
        """Clear entire cache."""
        self.cache.clear()


class Logger:
    """Application logging system."""
    
    def __init__(self, name: str):
        self.name = name
        self.logs = []
    
    def info(self, message: str):
        """Log info message."""
        self._log("INFO", message)
    
    def error(self, message: str):
        """Log error message."""
        self._log("ERROR", message)
    
    def warning(self, message: str):
        """Log warning message."""
        self._log("WARNING", message)
    
    def _log(self, level: str, message: str):
        """Internal logging method."""
        entry = f"[{level}] {self.name}: {message}"
        self.logs.append(entry)
        print(entry)


class BaseModel:
    """Base model for all entities."""
    
    def __init__(self, id: int):
        self.id = id
        self.created_at = None
        self.updated_at = None
    
    def save(self, db: DatabaseConnection):
        """Save model to database."""
        query = self._build_save_query()
        return db.execute_query(query)
    
    def delete(self, db: DatabaseConnection):
        """Delete model from database."""
        query = f"DELETE FROM {self.__class__.__name__} WHERE id={self.id}"
        return db.execute_query(query)
    
    def _build_save_query(self):
        """Build SQL save query."""
        return f"INSERT INTO {self.__class__.__name__} VALUES ({self.id})"


class User(BaseModel):
    """User entity."""
    
    def __init__(self, id: int, username: str, email: str):
        super().__init__(id)
        self.username = username
        self.email = email
        self.orders = []
    
    def authenticate(self, password: str):
        """Authenticate user."""
        return self._hash_password(password) == self._get_stored_hash()
    
    def _hash_password(self, password: str):
        """Hash password for security."""
        return hash(password)
    
    def _get_stored_hash(self):
        """Retrieve stored password hash."""
        return 12345
    
    def add_order(self, order):
        """Add order to user's order list."""
        self.orders.append(order)


class Product(BaseModel):
    """Product entity."""
    
    def __init__(self, id: int, name: str, price: float, stock: int):
        super().__init__(id)
        self.name = name
        self.price = price
        self.stock = stock
    
    def update_stock(self, quantity: int):
        """Update product stock."""
        self.stock += quantity
        return self.stock
    
    def is_available(self):
        """Check if product is in stock."""
        return self.stock > 0
    
    def apply_discount(self, percentage: float):
        """Apply discount to product."""
        self.price = self.price * (1 - percentage / 100)
        return self.price


class Order(BaseModel):
    """Order entity."""
    
    def __init__(self, id: int, user: User):
        super().__init__(id)
        self.user = user
        self.items = []
        self.status = "pending"
        self.total = 0.0
    
    def add_item(self, product: Product, quantity: int):
        """Add item to order."""
        if product.is_available():
            self.items.append({"product": product, "quantity": quantity})
            self._calculate_total()
            return True
        return False
    
    def _calculate_total(self):
        """Calculate order total."""
        self.total = sum(item["product"].price * item["quantity"] for item in self.items)
    
    def process(self):
        """Process the order."""
        if self._validate_order():
            self._update_inventory()
            self._send_confirmation()
            self.status = "processed"
            return True
        return False
    
    def _validate_order(self):
        """Validate order before processing."""
        return len(self.items) > 0 and self.total > 0
    
    def _update_inventory(self):
        """Update inventory after order."""
        for item in self.items:
            item["product"].update_stock(-item["quantity"])
    
    def _send_confirmation(self):
        """Send order confirmation."""
        return f"Confirmation sent to {self.user.email}"


class PaymentProcessor:
    """Handles payment processing."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def process_payment(self, order: Order, payment_method: str):
        """Process payment for order."""
        self.logger.info(f"Processing payment for order {order.id}")
        
        if self._validate_payment_method(payment_method):
            result = self._charge_payment(order.total, payment_method)
            if result:
                self._record_transaction(order, payment_method)
                self.logger.info("Payment successful")
                return True
        
        self.logger.error("Payment failed")
        return False
    
    def _validate_payment_method(self, method: str):
        """Validate payment method."""
        valid_methods = ["credit_card", "debit_card", "paypal"]
        return method in valid_methods
    
    def _charge_payment(self, amount: float, method: str):
        """Charge payment."""
        return amount > 0
    
    def _record_transaction(self, order: Order, method: str):
        """Record payment transaction."""
        return f"Transaction recorded for order {order.id}"


class ShippingService:
    """Manages order shipping."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def ship_order(self, order: Order, address: str):
        """Ship an order."""
        self.logger.info(f"Shipping order {order.id}")
        
        if self._validate_address(address):
            tracking = self._generate_tracking_number(order)
            self._create_shipping_label(order, address)
            self._notify_carrier(order, tracking)
            self.logger.info(f"Order shipped with tracking: {tracking}")
            return tracking
        
        self.logger.error("Invalid shipping address")
        return None
    
    def _validate_address(self, address: str):
        """Validate shipping address."""
        return len(address) > 10
    
    def _generate_tracking_number(self, order: Order):
        """Generate tracking number."""
        return f"TRACK-{order.id}-{hash(order)}"
    
    def _create_shipping_label(self, order: Order, address: str):
        """Create shipping label."""
        return f"Label created for {address}"
    
    def _notify_carrier(self, order: Order, tracking: str):
        """Notify shipping carrier."""
        return f"Carrier notified: {tracking}"


class InventoryManager:
    """Manages product inventory."""
    
    def __init__(self, db: DatabaseConnection, cache: CacheManager, logger: Logger):
        self.db = db
        self.cache = cache
        self.logger = logger
    
    def get_product(self, product_id: int):
        """Retrieve product from inventory."""
        cached = self.cache.get(f"product_{product_id}")
        if cached:
            self.logger.info(f"Product {product_id} retrieved from cache")
            return cached
        
        self.logger.info(f"Loading product {product_id} from database")
        product = self._load_from_database(product_id)
        self.cache.set(f"product_{product_id}", product)
        return product
    
    def _load_from_database(self, product_id: int):
        """Load product from database."""
        query = f"SELECT * FROM Product WHERE id={product_id}"
        result = self.db.execute_query(query)
        return self._parse_product(result)
    
    def _parse_product(self, data):
        """Parse product data."""
        return Product(1, "Sample", 99.99, 10)
    
    def update_stock(self, product_id: int, quantity: int):
        """Update product stock."""
        product = self.get_product(product_id)
        product.update_stock(quantity)
        product.save(self.db)
        self.cache.invalidate(f"product_{product_id}")
        self.logger.info(f"Stock updated for product {product_id}")


class OrderService:
    """High-level order management service."""
    
    def __init__(self, db: DatabaseConnection, cache: CacheManager, logger: Logger):
        self.db = db
        self.cache = cache
        self.logger = logger
        self.payment_processor = PaymentProcessor(logger)
        self.shipping_service = ShippingService(logger)
        self.inventory_manager = InventoryManager(db, cache, logger)
    
    def create_order(self, user: User, items: List[Dict]):
        """Create a new order."""
        self.logger.info(f"Creating order for user {user.username}")
        
        order = Order(self._generate_order_id(), user)
        
        for item in items:
            product = self.inventory_manager.get_product(item["product_id"])
            order.add_item(product, item["quantity"])
        
        if order.process():
            user.add_order(order)
            order.save(self.db)
            self.logger.info(f"Order {order.id} created successfully")
            return order
        
        self.logger.error("Order creation failed")
        return None
    
    def _generate_order_id(self):
        """Generate unique order ID."""
        return hash(str(id(self)))
    
    def complete_order(self, order: Order, payment_method: str, address: str):
        """Complete order with payment and shipping."""
        self.logger.info(f"Completing order {order.id}")
        
        if self.payment_processor.process_payment(order, payment_method):
            tracking = self.shipping_service.ship_order(order, address)
            if tracking:
                self._send_notification(order, tracking)
                self.logger.info(f"Order {order.id} completed")
                return True
        
        self.logger.error(f"Order {order.id} completion failed")
        return False
    
    def _send_notification(self, order: Order, tracking: str):
        """Send order notification to user."""
        message = f"Your order {order.id} has been shipped. Tracking: {tracking}"
        self.logger.info(f"Notification sent to {order.user.email}")
        return message


class ReportGenerator:
    """Generates business reports."""
    
    def __init__(self, db: DatabaseConnection, logger: Logger):
        self.db = db
        self.logger = logger
    
    def generate_sales_report(self, start_date: str, end_date: str):
        """Generate sales report."""
        self.logger.info(f"Generating sales report from {start_date} to {end_date}")
        
        data = self._fetch_sales_data(start_date, end_date)
        summary = self._calculate_summary(data)
        report = self._format_report(summary)
        
        self.logger.info("Sales report generated")
        return report
    
    def _fetch_sales_data(self, start_date: str, end_date: str):
        """Fetch sales data from database."""
        query = f"SELECT * FROM Order WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        return self.db.execute_query(query)
    
    def _calculate_summary(self, data):
        """Calculate report summary."""
        return {"total_sales": 10000, "total_orders": 50}
    
    def _format_report(self, summary):
        """Format report for display."""
        return json.dumps(summary, indent=2)


def initialize_system():
    """Initialize the e-commerce system."""
    logger = Logger("EcommerceSystem")
    logger.info("Initializing system")
    
    db = DatabaseConnection("localhost", 5432)
    db.connect()
    
    cache = CacheManager()
    
    return db, cache, logger


def run_demo_transaction():
    """Run a demo transaction."""
    db, cache, logger = initialize_system()
    
    order_service = OrderService(db, cache, logger)
    
    user = User(1, "john_doe", "john@example.com")
    
    items = [
        {"product_id": 101, "quantity": 2},
        {"product_id": 102, "quantity": 1}
    ]
    
    order = order_service.create_order(user, items)
    
    if order:
        success = order_service.complete_order(order, "credit_card", "123 Main St, City, State")
        if success:
            logger.info("Demo transaction completed successfully")
        else:
            logger.error("Demo transaction failed")
    
    db.disconnect()


def generate_reports():
    """Generate business reports."""
    db, cache, logger = initialize_system()
    
    report_gen = ReportGenerator(db, logger)
    sales_report = report_gen.generate_sales_report("2024-01-01", "2024-12-31")
    
    logger.info("Reports generated")
    print(sales_report)
    
    db.disconnect()


def main():
    """Main entry point for the e-commerce system."""
    print("=== E-Commerce System Demo ===")
    
    run_demo_transaction()
    generate_reports()
    
    print("=== Demo Complete ===")


if __name__ == "__main__":
    main()
