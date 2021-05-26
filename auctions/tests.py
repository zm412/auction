from django.test import TestCase
from django.urls import reverse
from datetime import timedelta, datetime

# Create your tests here.

from .models import User, Category, Product, Comment, Bids, Auction

class CategoryTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='TestUsersName',
            email='test1email@gmail.com',
            password='Aa@123456'
        )
        self.user.save()
        self.categoryTest= Category.objects.create(name="animal")
        self.product = self.user.seller.create(
            category=self.categoryTest,
            name='Test1',
            title='Test1Title',
            description='test1Description',
        )
        self.auction = self.product.prod_auction.create(
            start_price = 120,
            start_date = datetime.now(),
            finish_date = datetime.now()+timedelta(2)
        )
        self.userNotSeller = User.objects.create_user(
            'TestNotSeller',
            'test2email@gmail.com',
            'Aa@123456'
        )
        self.comment = self.auction.comm_item.create(
            user=self.userNotSeller,
            comment='comment TEST1',
        )
        self.bid = self.auction.bids_item.create(
            bid=125,
            user=self.userNotSeller,
            bids_time=datetime.now()
        )
        self.client.login(username='TestUsersName', password='Aa@123456')

    def test_correct_auth(self):
        login = self.client.login(username='TestUsersName',password='Aa@123456')
        resp = self.client.post(reverse('login'))
        print(resp, 'L;LKLKJ;LKJLKJLKJ')

        self.assertEqual(str(resp.context['user']), 'TestUsersName')
        self.assertEqual(resp.status_code, 200)
    def test_wrong_username(self):
        response = self.client.post('/login/', {'username': 'wrong', 'password':  'Aa@123456'})
        self.assertFalse(response.data['authenticated'])
    def test_wrong_pssword(self):
        response = self.client.post('/login/', {'username': 'TestUsersName', 'password': 'wrong'})
        self.assertFalse(response.data['authenticated'])


    def test_user_exists(self):
        user1 = User.objects.get(username='TestUsersName')
        self.assertEqual(user1.username, 'TestUsersName')
    def test_check_category(self):
        category = Category.objects.get(name='animal')
        self.assertEqual(category.name, 'animal')
    def test_check_product(self):
        product = Product.objects.get(user=self.user)
        self.assertEqual(product.description, 'test1Description')
    def test_check_auction(self):
        auction = Auction.objects.get(product=self.product)
        self.assertEqual(auction.start_price, 120)
    def test_check_comment(self):
        bid = Bids.objects.get(auction=self.auction)
        self.assertEqual(bid.bid,  125)
        """
    def test_check_put_in(self):
        response = self.client.get('/all/')
        self.assertEqual(response.data, {'tasks': []})
        """




