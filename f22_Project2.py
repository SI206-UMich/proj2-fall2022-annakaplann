#Name: Anna Kaplan
#UM ID: 23290438
#Worked With: Madison Leidner & Lauren Snerson

from xml.sax import parseString
from bs4 import BeautifulSoup
import re
import os
import csv
import unittest

def get_listings_from_search_results(html_file):
    """
    Write a function that creates a BeautifulSoup object on html_file. Parse
    through the object and return a list of tuples containing:
     a string of the title of the listing,
     an int of the cost to rent for one night,
     and a string of the listing id number
    in the format given below. Make sure to turn costs into ints.

    The listing id is found in the url of a listing. For example, for
        https://www.airbnb.com/rooms/1944564
    the listing id is 1944564.
.

    [
        ('Title of Listing 1', 'Cost 1', 'Listing ID 1'),  # format
        ('Loft in Mission District', 210, '1944564'),  # example
    ]
    """
    f = open(html_file, 'r')
    contents = f.read()
    f.close()
    soup = BeautifulSoup(contents, 'html.parser')

    title_lst = []
    price_lst = []
    id_lst = []

    div_tags = soup.find_all('div', class_ = 't1jojoys dir dir-ltr')
    span_tags = soup.find_all('span', class_ = '_tyxjp1')

    for tag in div_tags:
        title = tag.text.strip()
        title_lst.append(title)
        id = tag.get('id').strip('title_')
        id_lst.append(id)
    for tag in span_tags:
        price = tag.text.strip('$')
        price_lst.append(int(price))
    
    final_lst = []
    i = 0
    while i < len(title_lst):
        final_lst.append((title_lst[i], price_lst[i], id_lst[i]))
        i += 1

    return final_lst


def get_listing_information(listing_id):
    """
    Write a function to return relevant information in a tuple from an Airbnb listing id.
    NOTE: Use the static files in the html_files folder, do NOT send requests to the actual website.
    Information we're interested in:
        string - Policy number: either a string of the policy number, "Pending", or "Exempt"
            This field can be found in the section about the host.
            Note that this is a text field the lister enters, this could be a policy number, or the word
            "pending" or "exempt" or many others. Look at the raw data, decide how to categorize them into
            the three categories.
        string - Place type: either "Entire Room", "Private Room", or "Shared Room"
            Note that this data field is not explicitly given from this page. Use the
            following to categorize the data into these three fields.
                "Private Room": the listing subtitle has the word "private" in it
                "Shared Room": the listing subtitle has the word "shared" in it
                "Entire Room": the listing subtitle has neither the word "private" nor "shared" in it
        int - Number of bedrooms
.
    (
        policy number,
        place type,
        number of bedrooms
    )
    """
    f = open('html_files/listing_'+listing_id+'.html', 'r')
    contents = f.read()
    f.close()
    soup = BeautifulSoup(contents, 'html.parser')

    li_tags = soup.find_all('li', class_ = 'f19phm7j dir dir-ltr')
    div_tags = soup.find_all('div', class_ = '_cv5qq4')
    li_tags2 = soup.find_all('li', class_ = 'l7n4lsf dir dir-ltr')
    
    for tag in li_tags:
        if "Policy number" in tag.text.strip():
            find_number = tag.find('span', class_ = 'll4r2nl dir dir-ltr')
            policy_number = find_number.text.strip()
            if "pending" in policy_number.lower():
                policy_number = "Pending"
            elif "not" in policy_number.lower():
                policy_number = "Exempt"
    for tag in div_tags:
        find_place = tag.find('h2', class_ = '_14i3z6h')
        if "private" in find_place.text.strip().lower():
            place_type = "Private Room"
        elif "shared" in find_place.text.strip().lower():
            place_type = "Shared Room"
        else:
            place_type = "Entire Room"
    num_bedrooms = 0
    for tag in li_tags2:
        find_bedrooms = tag.find_all('span')
        for item in find_bedrooms:
            if "bedroom" in tag.text.strip():
                num_bedrooms = re.sub('\D', "", tag.text.strip())
    
    return (policy_number, place_type, int(num_bedrooms))


def get_detailed_listing_database(html_file):
    """
    Write a function that calls the above two functions in order to return
    the complete listing information using the functions you???ve created.
    This function takes in a variable representing the location of the search results html file.
    The return value should be in this format:


    [
        (Listing Title 1,Cost 1,Listing ID 1,Policy Number 1,Place Type 1,Number of Bedrooms 1),
        (Listing Title 2,Cost 2,Listing ID 2,Policy Number 2,Place Type 2,Number of Bedrooms 2),
        ...
    ]
    """
    detailed_result = []
    function_one = get_listings_from_search_results(html_file)
    for value in function_one:
        function_two = get_listing_information(value[2])
        detailed_result.append((value[0], value[1], value[2], function_two[0], function_two[1], function_two[2]))
    
    return detailed_result


def write_csv(data, filename):
    """
    Write a function that takes in a list of tuples (called data, i.e. the
    one that is returned by get_detailed_listing_database()), sorts the tuples in
    ascending order by cost, writes the data to a csv file, and saves it
    to the passed filename. The first row of the csv should contain
    "Listing Title", "Cost", "Listing ID", "Policy Number", "Place Type", "Number of Bedrooms",
    respectively as column headers. For each tuple in data, write a new
    row to the csv, placing each element of the tuple in the correct column.

    When you are done your CSV file should look like this:

    Listing Title,Cost,Listing ID,Policy Number,Place Type,Number of Bedrooms
    title1,cost1,id1,policy_number1,place_type1,num_bedrooms1
    title2,cost2,id2,policy_number2,place_type2,num_bedrooms2
    title3,cost3,id3,policy_number3,place_type3,num_bedrooms3
    ...

    In order of least cost to most cost.

    This function should not return anything.
    """
    f = open(filename, 'w')
    header = 'Listing Title,Cost,Listing ID,Policy Number,Place Type,Number of Bedrooms \n'
    f.write(header)
    writer = csv.writer(f)
    sorted_data = sorted(data, key = lambda x: x[1])
    writer.writerows(sorted_data)
    f.close()


def check_policy_numbers(data):
    """
    Write a function that takes in a list of tuples called data, (i.e. the one that is returned by
    get_detailed_listing_database()), and parses through the policy number of each, validating the
    policy number matches the policy number format. Ignore any pending or exempt listings.
    Return the listing numbers with respective policy numbers that do not match the correct format.
        Policy numbers are a reference to the business license San Francisco requires to operate a
        short-term rental. These come in two forms, where # is a number from [0-9]:
            20##-00####STR
            STR-000####
    .
    Return value should look like this:
    [
        listing id 1,
        listing id 2,
        ...
    ]

    """
    pattern1 = '20[\d]{2}-00[\d]{4}STR'
    pattern2 = 'STR-000[\d]{4}'
    final_lst = []
    for item in data:
        if item[3] != "Pending" and item[3] != "Exempt":
            lst1 = re.findall(pattern1, item[3])
            lst2 = re.findall(pattern2, item[3])
            if len(lst1) + len(lst2) == 0:
                final_lst.append(item[2])
    return final_lst


def extra_credit(listing_id):
    """
    There are few exceptions to the requirement of listers obtaining licenses
    before listing their property for short term leases. One specific exception
    is if the lister rents the room for less than 90 days of a year.

    Write a function that takes in a listing id, scrapes the 'reviews' page
    of the listing id for the months and years of each review (you can find two examples
    in the html_files folder), and counts the number of reviews the apartment had each year.
    If for any year, the number of reviews is greater than 90 (assuming very generously that
    every reviewer only stayed for one day), return False, indicating the lister has
    gone over their 90 day limit, else return True, indicating the lister has
    never gone over their limit.
    """
    f = open('html_files/listing_'+listing_id+'_reviews.html', 'r')
    contents = f.read()
    f.close()
    soup = BeautifulSoup(contents, 'html.parser')
    li_tags = soup.find_all('li', class_ = '_1f1oir5')
    review_dict = {}
    year_pattern = '.* (\d\d\d\d)'
    for tag in li_tags:
        date = tag.text.strip()
        year = re.findall(year_pattern, date)
        for yr in year:
            review_dict[yr] = review_dict.get(yr, 0) + 1
    for year in review_dict:
        if review_dict[year] > 90:
            return False
    return True


class TestCases(unittest.TestCase):

    def test_get_listings_from_search_results(self):
        # call get_listings_from_search_results("html_files/mission_district_search_results.html")
        # and save to a local variable
        listings = get_listings_from_search_results("html_files/mission_district_search_results.html")
        # check that the number of listings extracted is correct (20 listings)
        self.assertEqual(len(listings), 20)
        # check that the variable you saved after calling the function is a list
        self.assertEqual(type(listings), list)
        # check that each item in the list is a tuple
        for item in listings:
            self.assertEqual(type(item), tuple)
        # check that the first title, cost, and listing id tuple is correct (open the search results html and find it)
        self.assertEqual(listings[0][0], 'Loft in Mission District')
        self.assertEqual(listings[0][1], 210)
        self.assertEqual(listings[0][2], '1944564')
        # check that the last title is correct (open the search results html and find it)
        self.assertEqual(listings[19][0], 'Guest suite in Mission District')

    def test_get_listing_information(self):
        html_list = ["1623609",
                     "1944564",
                     "1550913",
                     "4616596",
                     "6600081"]
        # call get_listing_information for i in html_list:
        listing_informations = [get_listing_information(id) for id in html_list]
        # check that the number of listing information is correct (5)
        self.assertEqual(len(listing_informations), 5)
        for listing_information in listing_informations:
            # check that each item in the list is a tuple
            self.assertEqual(type(listing_information), tuple)
            # check that each tuple has 3 elements
            self.assertEqual(len(listing_information), 3)
            # check that the first two elements in the tuple are string
            self.assertEqual(type(listing_information[0]), str)
            self.assertEqual(type(listing_information[1]), str)
            # check that the third element in the tuple is an int
            self.assertEqual(type(listing_information[2]), int)
        # check that the first listing in the html_list has policy number 'STR-0001541'
        info = listing_informations[0]
        self.assertEqual(info[0], 'STR-0001541')
        # check that the last listing in the html_list is a "Private Room"
        info2 = listing_informations[-1]
        self.assertEqual(info2[1], 'Private Room')
        # check that the third listing has one bedroom
        info3 = listing_informations[2]
        self.assertEqual(listing_information[2], 1)

    def test_get_detailed_listing_database(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save it to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # check that we have the right number of listings (20)
        self.assertEqual(len(detailed_database), 20)
        for item in detailed_database:
            # assert each item in the list of listings is a tuple
            self.assertEqual(type(item), tuple)
            # check that each tuple has a length of 6
            self.assertEqual(len(item), 6)
        # check that the first tuple is made up of the following:
        # 'Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1
        self.assertEqual(detailed_database[0], ('Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1))
        # check that the last tuple is made up of the following:
        # 'Guest suite in Mission District', 238, '32871760', 'STR-0004707', 'Entire Room', 1
        self.assertEqual(detailed_database[-1], ('Guest suite in Mission District', 238, '32871760', 'STR-0004707', 'Entire Room', 1))
    
    def test_write_csv(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call write csv on the variable you saved
        write_csv(detailed_database, "test.csv")
        # read in the csv that you wrote
        csv_lines = []
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.csv'), 'r') as f:
            csv_reader = csv.reader(f)
            for i in csv_reader:
                csv_lines.append(i)
        # check that there are 21 lines in the csv
        self.assertEqual(len(csv_lines), 21)
        # check that the header row is correct
        self.assertEqual(csv_lines[0], ['Listing Title', 'Cost', 'Listing ID', 'Policy Number', 'Place Type', 'Number of Bedrooms '])
        # check that the next row is Private room in Mission District,82,51027324,Pending,Private Room,1
        self.assertEqual(csv_lines[1],['Private room in Mission District', '82', '51027324', 'Pending', 'Private Room', '1'])
        # check that the last row is Apartment in Mission District,399,28668414,Pending,Entire Room,2
        self.assertEqual(csv_lines[-1],['Apartment in Mission District', '399', '28668414', 'Pending', 'Entire Room', '2'])
    
    def test_check_policy_numbers(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call check_policy_numbers on the variable created above and save the result as a variable
        invalid_listings = check_policy_numbers(detailed_database)
        # check that the return value is a list
        self.assertEqual(type(invalid_listings), list)
        # check that there is exactly one element in the string
        self.assertEqual(len(invalid_listings), 1)
        # check that the element in the list is a string
        self.assertEqual(type(invalid_listings[0]), str)
        # check that the first element in the list is '16204265'
        self.assertEqual(invalid_listings[0], '16204265')
    
if __name__ == '__main__':
    database = get_detailed_listing_database("html_files/mission_district_search_results.html")
    write_csv(database, "airbnb_dataset.csv")
    check_policy_numbers(database)
    unittest.main(verbosity=2)
