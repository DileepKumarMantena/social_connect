"""
AI User and Company Generator Service
Provides intelligent suggestions for user and company creation
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib

class AIUserGenerator:
    """AI-powered user and company generation service"""
    
    def __init__(self):
        self.first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
            "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
            "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
            "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
            "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle",
            "Kenneth", "Laura", "Kevin", "Sarah", "Brian", "Kimberly", "George", "Deborah",
            "Edward", "Dorothy", "Ronald", "Lisa", "Timothy", "Nancy", "Jason", "Karen",
            "Jeffrey", "Betty", "Ryan", "Helen", "Jacob", "Sandra", "Gary", "Donna",
            "Nicholas", "Carol", "Eric", "Ruth", "Jonathan", "Sharon", "Stephen", "Michelle",
            "Larry", "Laura", "Justin", "Sarah", "Scott", "Kimberly", "Brandon", "Deborah",
            "Benjamin", "Dorothy", "Samuel", "Lisa", "Frank", "Nancy", "Raymond", "Karen",
            "Gregory", "Betty", "Alexander", "Helen", "Patrick", "Sandra", "Jack", "Donna"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
            "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
            "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
            "Flores", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell",
            "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards",
            "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan",
            "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard",
            "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks",
            "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson",
            "Coleman", "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores",
            "Washington", "Butler", "Simmons", "Foster", "Gonzales", "Bryant", "Alexander",
            "Russell", "Griffin", "Diaz", "Hayes", "Myers", "Ford", "Hamilton", "Graham",
            "Sullivan", "Wallace", "Woods", "Cole", "West", "Jordan", "Owens", "Reynolds"
        ]
        
        self.company_prefixes = [
            "Tech", "Digital", "Smart", "Global", "Innovation", "Advanced", "Modern",
            "Creative", "Strategic", "Dynamic", "Elite", "Premier", "Pro", "Max",
            "Next", "Future", "Quantum", "Cyber", "Data", "Cloud", "Mobile", "Web"
        ]
        
        self.company_suffixes = [
            "Solutions", "Systems", "Technologies", "Innovations", "Dynamics", "Consulting",
            "Services", "Group", "Corp", "Inc", "LLC", "Labs", "Works", "Hub", "Net",
            "Soft", "Ware", "Tech", "Digital", "Media", "Creative", "Design", "Studio",
            "Agency", "Partners", "Alliance", "Ventures", "Enterprises", "Industries"
        ]
        
        self.domains = [
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "company.com",
            "business.com", "tech.com", "mail.com", "email.com", "work.com"
        ]
        
        self.job_titles = [
            "Software Engineer", "Product Manager", "Data Analyst", "Marketing Manager",
            "Sales Representative", "Business Analyst", "Project Manager", "UX Designer",
            "Web Developer", "Mobile Developer", "DevOps Engineer", "QA Engineer",
            "Technical Writer", "Content Manager", "Social Media Manager", "HR Manager",
            "Financial Analyst", "Account Manager", "Customer Success", "Support Specialist",
            "Operations Manager", "Logistics Coordinator", "Procurement Specialist",
            "Research Analyst", "Business Development", "Partnership Manager"
        ]
        
        self.departments = [
            "Engineering", "Marketing", "Sales", "Operations", "HR", "Finance",
            "Product", "Design", "Support", "Legal", "IT", "Research", "Analytics"
        ]

    def generate_username(self, first_name: str, last_name: str) -> str:
        """Generate username from name"""
        base_username = f"{first_name.lower()}.{last_name.lower()}"
        
        # Add random number if username exists
        if random.random() < 0.3:  # 30% chance of having number
            base_username += str(random.randint(1, 999))
        
        return base_username

    def generate_email(self, first_name: str, last_name: str, company_domain: Optional[str] = None) -> str:
        """Generate email address"""
        if company_domain:
            # Company email
            patterns = [
                f"{first_name.lower()}.{last_name.lower()}@{company_domain}",
                f"{first_name.lower()[0]}{last_name.lower()}@{company_domain}",
                f"{first_name.lower()}_{last_name.lower()}@{company_domain}",
                f"{first_name.lower()}{random.randint(1, 999)}@{company_domain}"
            ]
        else:
            # Personal email
            patterns = [
                f"{first_name.lower()}.{last_name.lower()}@{random.choice(self.domains)}",
                f"{first_name.lower()}{random.randint(1, 999)}@{random.choice(self.domains)}",
                f"{first_name.lower()}{last_name.lower()[0]}@{random.choice(self.domains)}"
            ]
        
        return random.choice(patterns)

    def generate_phone_number(self) -> str:
        """Generate US phone number"""
        area_codes = ["212", "646", "917", "718", "347", "929", "516", "631", "914", "845"]
        area_code = random.choice(area_codes)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        return f"({area_code}) {exchange}-{number}"

    def generate_address(self) -> Dict[str, str]:
        """Generate US address"""
        streets = [
            "Main St", "Oak Ave", "Elm St", "Maple Ave", "Cedar St", "Pine St",
            "Washington St", "Lincoln Ave", "Park Ave", "Broadway", "5th Ave",
            "Madison Ave", "Wall St", "Spring St", "Canal St", "Houston St"
        ]
        
        cities = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
            "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"
        ]
        
        states = [
            "NY", "CA", "IL", "TX", "AZ", "PA", "FL", "OH", "GA", "NC",
            "MI", "NJ", "VA", "WA", "MA", "TN", "IN", "MO", "MD", "CO"
        ]
        
        street_number = random.randint(1, 9999)
        street = random.choice(streets)
        city = random.choice(cities)
        state = random.choice(states)
        zip_code = f"{random.randint(10000, 99999)}"
        
        return {
            "street": f"{street_number} {street}",
            "city": city,
            "state": state,
            "zip": zip_code,
            "full_address": f"{street_number} {street}, {city}, {state} {zip_code}"
        }

    def generate_company(self, industry: Optional[str] = None) -> Dict[str, str]:
        """Generate company information"""
        if industry:
            industry_prefixes = {
                "Technology": ["Tech", "Digital", "Cyber", "Quantum", "Cloud"],
                "Healthcare": ["Med", "Health", "Bio", "Pharma", "Care"],
                "Finance": ["Fin", "Capital", "Wealth", "Invest", "Money"],
                "Retail": ["Shop", "Store", "Market", "Retail", "Trade"],
                "Education": ["Edu", "Learn", "Academy", "School", "College"],
                "Manufacturing": ["Manu", "Factory", "Industrial", "Prod", "Works"]
            }
            prefixes = industry_prefixes.get(industry, self.company_prefixes)
        else:
            prefixes = self.company_prefixes
        
        prefix = random.choice(prefixes)
        suffix = random.choice(self.company_suffixes)
        company_name = f"{prefix}{suffix}"
        
        # Generate company domain
        domain_suffixes = ["com", "net", "org", "io", "tech", "co", "ai"]
        domain_suffix = random.choice(domain_suffixes)
        company_domain = f"{company_name.lower().replace(' ', '')}.{domain_suffix}"
        
        # Generate company details
        industries = ["Technology", "Healthcare", "Finance", "Retail", "Education", "Manufacturing"]
        company_industry = industry or random.choice(industries)
        
        company_sizes = ["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]
        company_size = random.choice(company_sizes)
        
        # Generate company address
        address = self.generate_address()
        
        # Generate company phone
        phone = self.generate_phone_number()
        
        return {
            "name": company_name,
            "domain": company_domain,
            "industry": company_industry,
            "size": company_size,
            "description": f"Leading {company_industry} company specializing in innovative solutions",
            "address": address,
            "phone": phone,
            "founded": str(random.randint(1990, 2023)),
            "revenue": f"${random.randint(1, 1000)}M"
        }

    def generate_user(self, role: str = "user", company_id: Optional[int] = None, 
                     company_domain: Optional[str] = None) -> Dict[str, str]:
        """Generate user information"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        full_name = f"{first_name} {last_name}"
        
        username = self.generate_username(first_name, last_name)
        email = self.generate_email(first_name, last_name, company_domain)
        phone = self.generate_phone_number()
        address = self.generate_address()
        
        # Generate job-related info
        job_title = random.choice(self.job_titles)
        department = random.choice(self.departments)
        
        # Generate password
        password = self.generate_secure_password()
        
        # Generate access expiration
        days_until_expiration = random.randint(30, 365)
        access_expires_at = (datetime.utcnow() + timedelta(days=days_until_expiration)).isoformat()
        
        # User type based on role
        user_types = {
            "super_admin": "platform_owner",
            "admin": "tenant_user",
            "user": "tenant_employee"
        }
        user_type = user_types.get(role, "tenant_employee")
        
        return {
            "username": username,
            "email": email,
            "name": full_name,
            "password": password,
            "password_hash": hashlib.sha256(password.encode()).hexdigest(),
            "role": role,
            "companyid": company_id or 1,
            "user_type": user_type,
            "activitystatus": True,
            "access_expires_at": access_expires_at,
            "created_by": "ai_generator",
            "phone": phone,
            "address": address,
            "job_title": job_title,
            "department": department,
            "hire_date": (datetime.utcnow() - timedelta(days=random.randint(1, 1000))).isoformat(),
            "salary": f"${random.randint(40000, 150000)}"
        }

    def generate_secure_password(self) -> str:
        """Generate secure password"""
        import secrets
        import string
        
        # Generate password with at least 8 characters, including uppercase, lowercase, digits, and special chars
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(characters) for _ in range(12))
        
        # Ensure it has at least one uppercase, one lowercase, one digit, and one special character
        if not any(c.isupper() for c in password):
            password = password[:-1] + random.choice(string.ascii_uppercase)
        if not any(c.islower() for c in password):
            password = password[:-1] + random.choice(string.ascii_lowercase)
        if not any(c.isdigit() for c in password):
            password = password[:-1] + random.choice(string.digits)
        if not any(c in "!@#$%^&*" for c in password):
            password = password[:-1] + random.choice("!@#$%^&*")
        
        return password

    def generate_multiple_users(self, count: int, role_distribution: Optional[Dict[str, int]] = None,
                               company_id: Optional[int] = None, company_domain: Optional[str] = None) -> List[Dict]:
        """Generate multiple users with role distribution"""
        users = []
        
        if role_distribution:
            for role, role_count in role_distribution.items():
                for _ in range(role_count):
                    user = self.generate_user(role, company_id, company_domain)
                    users.append(user)
        else:
            # Default distribution: 70% users, 25% admins, 5% super_admins
            for i in range(count):
                if i < count * 0.05:
                    role = "super_admin"
                elif i < count * 0.30:
                    role = "admin"
                else:
                    role = "user"
                
                user = self.generate_user(role, company_id, company_domain)
                users.append(user)
        
        return users

    def generate_multiple_companies(self, count: int, industry: Optional[str] = None) -> List[Dict]:
        """Generate multiple companies"""
        companies = []
        for _ in range(count):
            company = self.generate_company(industry)
            companies.append(company)
        return companies

# Global instance
ai_generator = AIUserGenerator()
