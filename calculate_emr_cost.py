#!/usr/bin/env python
#
# Copyright (c) 2016 Anup Ash . Contact anupash147@yahoo.com
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from __future__ import print_function

import sys
import time
import math
import yaml
import datetime

import util.ec2instancespricing

import boto3
import time
client = boto3.client('emr')


class Ec2timings:
    """
      The class is used to calculate the ec2 timings and generate an hourly scale. The price
      value is added and the final amount is calculated
    """

    def __init__(self, creation_ts, termination_ts, instance_price):
        self.lifetime = self._get_lifetime(creation_ts, termination_ts)
        self.cost = round((self.lifetime * instance_price),3)
        #print(instance_price)

    @staticmethod
    def _parse_dates(creation_ts, termination_ts):
        """
        :param creation_ts: the creation time string
        :param termination_ts: the termination time string
        :return: the lifetime of a single instance in hours
        """
        date_format = '%Y-%m-%d %H:%M:%S.%f+00:00'
        creation_ts = \
            time.mktime(time.strptime(creation_ts, date_format))
        termination_ts = \
            time.mktime(time.strptime(termination_ts, date_format))
        return creation_ts, termination_ts

    def _get_lifetime(self, creation_ts, termination_ts):
        """
        :param creation_ts: the creation time string
        :param termination_ts: the termination time string
        :return: the lifetime of a single instance in hours
        """
        (creation_ts, termination_ts) = \
            Ec2timings._parse_dates(creation_ts, termination_ts)
        #print(str(math.ceil((termination_ts - creation_ts) / 3600)) +" hrs")
        return math.ceil((termination_ts - creation_ts) / 3600)


class EMR_cost_calculator:

    def __init__(self, clusterid):
        self.totalcost = round(self.CalculateEmrCost(clusterid),3)

    def getGroupInstanceCosts(self, clusterid, instancegroupid,price):
        """
        :param clusterid        : this is the emr cluster id that you want to calculate
        :param instancegroupid  : the instancegroup id of MASTER/CORE/TASK nodes
        :param price            : ec2 price of that group.
        :return: the total price of all the instances in the instance group by hours. The hours consumed is
                 calculated by subtracting the EndDateTime from the CreationDateTime.
        """
        done = False
        marker = None
        total_cost = 0
        total_instances = 0

        while not done:
            if marker:
                response = client.list_instances(ClusterId=clusterid,InstanceGroupId=instancegroupid, Marker=marker)
            else:
                response = client.list_instances(ClusterId=clusterid,InstanceGroupId=instancegroupid)

            sub_total = 0
            for i in response['Instances']:
                total_instances = total_instances + 1
                c = Ec2timings(str(i['Status']['Timeline']['CreationDateTime']),str(i['Status']['Timeline']['EndDateTime']),price).cost
                sub_total += c
            try:
                marker = response['Marker']

            except KeyError:
                done = True

            total_cost += sub_total


        print ("Total instances used : " +str(total_instances))
        return total_cost


    def get_instance_cost_includes_emr_cost(self, instance_type,region="us-east-1"):
        """
        :param instance_type: type of ec2 instance
        :param region:  region
        :return: returns the total of ec2 and emr costs
        """
        emr_object = ec2instancespricing.get_emr_instances_prices(region,instance_type)
        # emr cost
        emr = emr_object['regions'][0]['instanceTypes'][0]['price']
        ec2 = emr_object['regions'][0]['instanceTypes'][1]['price']

        print ("Ec2 cost: $%s per/hr and EMR cost $%s per/hr" %(str(ec2),str(emr)))
        return emr + ec2


    def CalculateEmrCost(self, clusterid):
        """
        :param clusterid : this is the emr cluster id that you want to calculate
        :return: total cost of the cluster by calculating all the individual ec2 + emr costs.
        """
        response = client.list_instance_groups(ClusterId=clusterid)
        total_cost = 0
        for configs in response['InstanceGroups']:
            price = 0
            print ("=======" +configs['InstanceGroupType'] +"=======")
            if configs['Market'] == 'SPOT' :
                price = float(configs['BidPrice'])
            else:
                price = float(self.get_instance_cost_includes_emr_cost(configs['InstanceType']))

            print ("ID: " +configs['Id'] +"  Machine Type:" +configs['InstanceType'] +"  Market : " +configs['Market'] +"  Charged @" +str(round(price,3)))
            c = self.getGroupInstanceCosts(clusterid,configs['Id'],price)
            print ("Cost for this task group is $" +str(round(c,6)))
            total_cost += c

        return total_cost

def parseArgs():
    """parse command line arguments
    Returns:
        dictionary of parsed arguments
    """

    scriptname = "calculate_emr_cost.py"
    parser = argparse.ArgumentParser(scriptname)
    parser.add_argument('-c','--cluster-id,dest="clusterid",
                        help='Provide the emr cluster-id to calculate the total cost')
    parser.add_argument('-c','--region,dest="region",default='us-east-1',
                            help='Region where the emr cluster is running')
    return(vars(parser.parse_args()))


def main(**kwargs):
    """ calculate the emr cost
    Args:
        kwargs:
            cluster-id     -- the emr cluster-id to calculate the total cost
            region         -- region where teh emr cluster cost needs to be calcuated for
    Returns:
        total cost
    Examples:
        main(cluster-id='j-ABCDEF4521')
        main(**{'cluster-id': 'j-ABCDEF4521'})
        main(**args)
    """
    # get the startup params
    clusterid = kwargs.get('cluster-id')
    region = kwargs.get('region')

    print("your clusterid - %s in region %s" %(clusterid,region))
    #print("Total cost of the EMR $%s " %str(EMR_cost_calculator(clusterid).totalcost))
    print("=========================")



if __name__ == '__main__':
    """entry point for command line execution"""
    try:
        args = parseArgs()
        sys.exit(main(**args))
    except SystemExit:
        pass
    except:
        print('FAIL: unexpected error: %s' % sys.exc_info()[0])
